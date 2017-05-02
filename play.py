import random, datetime, config, roster
from utils import baseNarratives, log5, weightedChoice, emojis
from league import leagueMeans, STEAL_RATE, ADVANCE_EXTRA
from tweet import api
from wpa import winProb
from fractions import Fraction
from config import MONGO_URI
from pymongo import MongoClient

client = MongoClient(MONGO_URI)
gameColl = client.tweetball.games
teamColl = client.tweetball.teams

class Matchup(object):
	
	"""
	A Matchup object is initialized with two dictionaries, one for the batter 
	and one for the pitcher, containing each player's probability of individual
	outcomes. It uses Bill James' "Log 5" method to determine the probability of 
	each outcome when these players face each other. The genResult() function 
	uses the weightedChoice() function to pick an outcome based on these probabilities
	"""
	
	def __init__(self, batting, pitching):
		
		lgAvg = leagueMeans()
		
		for key in config.RESULT_TYPES:
		
			resultProb = log5(pitching[key], batting[key], lgAvg[key])
			
			setattr(self, key, resultProb)
			
	def genResult(self):
	
		return weightedChoice(self.__dict__)

class Event(object):
	
	"""
	Event objects are created for everything that happens in a game. They are passed
	relevant information about the game's current state and initialize with a type 
	(an outcome of some kind, e.g. 'double') and possess a function to calculate the 
	end state for every possible event.
	"""
	
	def __init__(self, **kwargs):
		
		"""
		An event is initialized with the verb string for what happens (e.g. 'doubles'),
		picks the proper function from the funcs dict which will return runner advancement 
		and other information, and sets the proper attributes. Events can be compiled in an
		inning object.
		"""
		
		funcs = {
				 'singles' : self.single, 
				 'doubles' : self.double,
				 'triples' : self.triple,
				 'homers' : self.homer,
				 'walks' : self.walk,
				 'strikes out' : self.strikeout,
				 'flies out' : self.flyout,
				 'lines out': self.lineout,
				 'grounds out': self.groundout,
				 'is hit by pitch' : self.hbp,
				 'error' : self.error,
				 'steals' : self.steal,
				 'enters to pitch' : self.bullpenCall,
				 'enters as a pinch hitter' : self.pinchHitter
				} 
		
		self.top = kwargs.pop('top')
		self.inning = kwargs.pop('inning')
		self.pitcher = kwargs.pop('pitcher')
		self.beginState = State.new(kwargs.pop('beginState'))
		self.battingTeam = kwargs.pop('battingTeam')
		self.pitchingTeam = kwargs.pop('pitchingTeam')
		self.type = kwargs.pop('type')
		self.func = funcs[self.type]
		self.endState = State.new(kwargs.pop('beginState'))
		self.func(self.endState)
		
		
	def genString(self):
		
		outfield = ['left', 'center', 'right']
		infield = ['first', 'second', 'third', 'shortstop']
		
		outs = [
					"lines out to {0}".format(random.choice(infield + outfield)),
					"flies out to {0}".format(random.choice(outfield)),
					"grounds out to {0}".format(random.choice(infield))
				]
				
		strings = {
					'strikeout' : 'strikes out',
					'sacrifice' : 'sacrifices',
					'GDP' : 'grounds into double play',
					'inPlayOut' : random.choice(outs),
					'single' : "singles to {0}".format(random.choice(outfield)),
					'double' : "doubles to {0}".format(random.choice(outfield)),
					'triple' : "triples to {0}".format(random.choice(outfield)),
					'HR' : "homers to {0}".format(random.choice(outfield)),
					'HBP' : "is hit by pitch",
					'BB' : "walks",
					'error' : "reaches on error"
				}
				
		return strings[self.type]
					
class State(object):

	def __init__(self, battingTeam, pitchingTeam, first=None, second=None, third=None, outs=0, runs=0):
	
		"""
		A State object contains Player objects for every player 
		on base and at the plate, as well as an integer representing the
		number of outs, and the batting team's number of runs and lineup object. 
		"""
		
		self.outs = outs
		self.battingTeam = battingTeam
		self.pitchingTeam = pitchingTeam
		self.advanceLog = ""
		self.pitcher = pitchingTeam.currentPitcher
		
		batter = self.battingTeam.atBat
		
		# Chain is a list that orders the batter and runners, with a fourth element to collect
		# runners who have scored via advancement. The State class __getattr__ will pull from 
		# State.chain if the batter, first, second, or third base runner is requested
		
		self.chain = [batter, first, second, third, []]
		
		# Forced is a list containing True or False is a runner is forced to advance. Batters
		# (forced[0]) and runners on first (forced[1]) are always forced to advance.
		
		self.forced = [True, True, False, False]
		
		if self.first:
			self.forced[2] = True
			
		if self.second and self.first:
			self.forced[3] = True
	
	def toDoc(self):
	
		"""
		Generates a BSON-friendly dict of relevant state attributes to save as
		an embedded doc in the event doc in the "events" array of the game doc
		"""
		
		doc = {
					'battingTeam' : self.battingTeam.ref,
					'pitchingTeam' : self.pitchingTeam.ref,
					'batter' : self.batter,
					'pitcher' : self.pitcher,
					'first' : self.first,
					'second' : self.second,
					'third' : self.third,
					'outs' : self.outs,
					'advancements' : self.advanceLog
			}
			
		return doc
	
	def __getattr__(self, key):
	
		"""
		If the state's batter or any baserunners are requested, __getattr__ will retrieve
		these from the chain attribute.
		"""
		
		slices = { 'batter' : 0, 'first' : 1, 'second' : 2, 'third' : 3, 'scored' : 4 }
		
		if key in slices:
			return self.chain[slices[key]]
		
		else:
			raise AttributeError
	
	def advance(self, runner, numBases=1):
	
		"""
		advance() will advance the passed runner position (a slice of the bases attribute) 
		the passed number of bases (an integer) per the dictates of baseball advancement
		logic. If there is no runner on the passed base, or a runner position greater
		than 3 is specified, it takes no action. Scoring runners are advanced to the 
		scoring list in position 4, and the State's runs attribute is updated.
		"""
		
		strings = ['', 'first', 'second', 'third']
		
		if not self.chain[runner] or runner > 3:
			return None
			
		if runner + numBases >= 4:
			self.advanceLog += "{0} scores. ".format(self.chain[runner].handle)
			self.chain[4].append(self.chain[runner])
			self.battingTeam.runs += 1
			self.chain[runner] = None
			
			if runner == 0:
				self.chain[runner] = self.battingTeam.newBatter()
		
		else:
			if runner != 0:
				self.advanceLog += "{0} to {1}. ".format(self.chain[runner].handle, strings[runner + numBases])
		
			self.chain[runner + numBases] = self.chain[runner]
			self.chain[runner] = None
			
			if runner == 0:
				self.chain[runner] = self.battingTeam.newBatter()
			
		#update the forced attribute to reflect new base state
		self.updateForced()
		
		return None
	
	def advanceAll(self, numBases):
	
		"""
		advanceAll() will advance every runner on base by numBases using the advance() method
		"""
		
		#Step backward through bases and advance runners
		for i in range(3,-1,-1):
			self.advance(i, numBases)
			
		return None
		
	def updateForced(self):
	
		"""
		updates the forced list based on the current state
		"""
		#Batter and runner on first are always forced
		self.forced[0], self.forced[1] = True, True
		
		self.forced[2], self.forced[3] = False, False
		
		if self.first and self.second:
			self.forced[2] = True
			self.forced[3] = True
		
		elif self.first:
			self.forced[2] = True
			
		return None	
	
	def makeEvents(self):
	
		"""
		Generator that yields Event objects		
		"""
		
		#Shuffle the check methods so they aren't always checked in same orders
		checks = [self.checkBullpen, self.checkPinchHitter, self.checkSteal]
		random.shuffle(checks)
		checkCalls = [func() for func in checks]
		
		for call in checkCalls:
			if call:
				event = call
				break
				
		
class PlateAppearance(object):
	
	def __init__(self, **kwargs):
		
		self.top = kwargs.pop('top')
		self.inning = kwargs.pop('inning')
		self.awayScore = kwargs.pop('awayScore')
		self.homeScore = kwargs.pop('homeScore')
		self.beginState = kwargs.pop('beginState')
		self.batter = kwargs.pop('batter')
		self.pitcher = kwargs.pop('pitcher')
		self.event = kwargs.pop('event')
		self.advancement = kwargs.pop('advancement')
		
		# advancement is a function that returns a tuple of the new base state and runs scored
		## To do:
		## should I use a singledispatch decorator to make multiple advancement functions depending on event?
		## should I add the batter to the baseState and drive the PAs that way
		## yes and yes. Each generated advancement function handles every base in a possible state
		## advancment methods are static methods of Event class (so maybe not singledispatch)
		## matchup function picks from a dict of these methods provided by Event class 
		## use kwargs to pass every possible piece of information down through the classes, only pass
		## to each what is needed 
		self.endState, self.runs = self.advancement(beginState)
		
		self.narratives = kwargs.pop('narratives')
		self.paTweet = kwargs.pop('paTweet')
	
	def tweetPA(self, replyTo):
	
		if self.top:
			half = emojis['top']
			aScore = self.awayScore + self.runs
			hScore = self.homeScore
			
		else:
			half = emojis['bottom']
			aScore = self.awayScore
			hScore = self.homeScore + self.runs
			
		inningString = "{0}{1}".format(half, self.inning)
		baseString = ""
		
		if self.baseState.first:
			baseString += emojis['first']
			
		else:
			baseString += emojis['empty']
			
		if self.baseState.second:
			baseString += emojis['second']
		
		else:
			baseString += emojis['empty']
			
		if self.baseState.third:
			baseString += emojis['third']
			
		else:
			baseString += emojis['empty']
		
		outString = emojis['out'] * self.baseState.outs
		outString += emojis['noOut'] * (2 - self.baseState.outs)
		
		narrative = str(self)
		
		if self.runs > 0:
			if self.top:
				scoreString = "{0} -- {1}".format(aScore, hScore)
			else:
				scoreString = "{0} -- {1}".format(hScore, aScore)
		else:
			scoreString = ""
		
		t = "{0} | {1} | {2} |\r\n {3}. {4}".format(inningString, baseString, outString, narrative, scoreString)
		
		if len(t) > 139:
			t = t[:139]
		
		tweetID = api.update_status(t, in_reply_to_status_id = replyTo).id
		
		return tweetID
	
	def __str__(self):
	
		description = '. '.join(self.narratives)
		
		return "{0}".format(description)

class Inning(object):

	def __init__(self, **kwargs):
		
		self.top = kwargs.pop('top')
		self.num = kwargs.pop('num')
		self.PAs = []
		self.terminating = None # implement logic for inning to determine this
		self.runs = 0
		self.battingTeam = kwargs.pop('battingTeam')
		self.pitchingTeam = kwargs.pop('pitchingTeam')
		
		
	def typePicker(self):
	
		"""
		Examines the state and previous PA and evaluates whether a steal, pitching change, 
		pinch hitter, or normal PA event should occur
		"""
		
		#Point system will accumulate points for event types based on various state traits
		steal, bullpen, pinch, pa = 0,0,0,0
		
		scoreDiff = abs(self.homeScore - self.awayScore)
		
		
class Game(object):

	def __init__(self, objectID):
		
		g = gameColl.find_one({ '_id' : objectID })
		
		self.homeTeam = roster.Team(g['home'])
		self.awayTeam = roster.Team(g['away'])
		self.innings = []
		self.startTime = g['start']
		self.complete = False
		
		first = {
					'top' : True,
					'num' : 1,
					'battingTeam' : self.awayTeam,
					'pitchingTeam' : self.homeTeam
				}
		
		self.innings.append(Inning(**first))
	
	