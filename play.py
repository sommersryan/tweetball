import random, datetime, config
from utils import baseNarratives, transitions, log5, weightedChoice, emojis
from league import leagueMeans, STEAL_RATE, ADVANCE_EXTRA
from tweet import api
from wpa import winProb
from fractions import Fraction
from copy import copy

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

	def __init__(self, battingLineup, pitchingLineup, batter, pitcher, first=None, second=None, third=None, outs=0, runs=0):
	
		"""
		A State object contains Player objects for every player 
		on base and at the plate, as well as an integer representing the
		number of outs, and the batting team's number of runs and lineup object. 
		"""
		
		# Note to self -- state includes pitcher. Uses a generator method that calls
		# methods to check various things -- whether there is a steal, pinch hitter,
		# bullpen call, etc, and uses Matchup class for batting events. Creates an 
		# event instance, and uses new() to store a copy of itself as beginState, calls an 
		# event function to modify itself, stores that as the endstate, and yields the event
		# for an iterator of the inning class to add to its events list 
		
		self.outs = outs
		self.runs = runs
		self.battingLineup = battingLineup
		self.pitchingLineup = pitchingLineup
		self.advanceLog = ""
		self.pitcher = pitcher
		
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
	
	@classmethod
	def new(cls, state):
	
		"""
		Initializes a new state from a previous one. Useful for storing copies
		of a state in the beginState and endState attributes of event objects and
		ensuring they won't be modified elsewhere. 
		"""
		
		kwargs = {
					'battingLineup' : state.battingLineup,
					'batter' : state.batter,
					'first' : state.first,
					'second' : state.second,
					'third' : state.third,
					'outs' : state.outs,
					'runs' : state.runs
				}
				
		inst = cls(**kwargs)
		
		return inst
	
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
			self.runs += 1
			self.chain[runner] = None
			
			if runner == 0:
				self.chain[runner] = self.battingLineup.newBatter()
		
		else:
			if runner != 0:
				self.advanceLog += "{0} to {1}. ".format(self.chain[runner].handle, strings[runner + numBases])
		
			self.chain[runner + numBases] = self.chain[runner]
			self.chain[runner] = None
			
			if runner == 0:
				self.chain[runner] = self.battingLineup.newBatter()
			
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
				
		if event:
			
		
				
		
		
		pass
		
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
		
	def advanceRunners(self, newBases, runs):
		
		oldState = self.baseState
		newState = BaseOutState()
		newState.outs = newBases[1]
		runners = oldState.queue()
		
		runners.insert(0, self.batter)
		
		for i in range(0, runs):
			
			self.narratives += ["{0} scores".format(str(runners.pop()))]
		
		if len(runners) > 0:
		
			if '3' in str(newBases[0]):
			
				newState.third = runners.pop()
				
				if newState.third != oldState.third:
					self.narratives += ["{0} to third".format(str(newState.third))]
				
		if len(runners) > 0:
		
			if '2' in str(newBases[0]):
			
				newState.second = runners.pop()
				
				if newState.second != oldState.second:
					self.narratives += ["{0} to second".format(str(newState.second))]
				
		if len(runners) > 0:
		
			if '1' in str(newBases[0]):
			
				newState.first = runners.pop()	

		if self.event.batterOut:
			try: 
				runners.pop()
			except IndexError:
				print(oldState)
				print(newBases)
				print(oldState.queue())
				
		return newState

	def getWPA(self):
	
		if self.top:
			startDiff = self.awayScore - self.homeScore
			endDiff = ((self.awayScore + self.runs) - self.homeScore)
			team = "V"
			
		else:
			startDiff = self.homeScore - self.awayScore
			endDiff = ((self.homeScore + self.runs) - self.awayScore)
			team = "H"
			
		if startDiff > 6:
			startDiff = 6
			
		if startDiff < -6:
			startDiff = -6
			
		if endDiff > 6:
			endDiff = 6
			
		if endDiff < -6:
			endDiff = -6
		
		if self.inning > 9:
			inn = 9
			
		else:
			inn = self.inning
		
		startState = (team, inn, *self.baseState.getState(), startDiff)
		startWP = winProb[startState]
		
		if self.endState.outs == 3:
		
			if self.top:
				team = "H"
				inn = self.inning
				
			else:
				team = "V"
				inn = self.inning + 1
			
			if inn > 9:
				inn = 9
			
			bases = BaseOutState()
			diff = -endDiff
			
			endState = (team, inn, *bases.getState(), diff)
			endWP = 1 - winProb[endState]
		
		else:
			
			endState = (team, inn, *self.endState.getState(), endDiff)
			
			try:
				endWP = winProb[endState]
			
			except KeyError:
				endWP = 1
			
		return endWP - startWP
		
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
		self.terminating = kwargs.pop('terminating')
		self.runs = 0
		self.homeScore = kwargs.pop('homeScore')
		self.awayScore = kwargs.pop('awayScore')
		self.awayTeam = kwargs.pop('awayTeam')
		self.homeTeam = kwargs.pop('homeTeam')
		
		self.battingTeam = self.awayTeam if self.top else self.homeTeam
		self.pitchingTeam = self.homeTeam if self.top else self.awayTeam
		
		
	def typePicker(self):
	
		"""
		Examines the state and previous PA and evaluates whether a steal, pitching change, 
		pinch hitter, or normal PA event should occur
		"""
		
		#Point system will accumulate points for event types based on various state traits
		steal, bullpen, pinch, pa = 0,0,0,0
		
		scoreDiff = abs(self.homeScore - self.awayScore)
		
		
class Game(object):

	def __init__(self, homeTeam, awayTeam):
	
		self.homeTeam = homeTeam
		self.awayTeam = awayTeam
		self.homeScore = 0
		self.awayScore = 0
		self.PAs = []
		self.inning = 1
		self.top = True
		self.startTime = datetime.datetime.now()
		self.complete = False
		
	def iterate(self, currentPA):
	
		self.PAs.append(currentPA)
		
		if self.top:
		
			self.awayScore += currentPA.runs
			batter = self.awayTeam.lineup.newBatter()
			pitcher = self.homeTeam.lineup.currentPitcher
			
			return PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, currentPA.endState, batter, pitcher)
			
		elif not self.top:
		
			self.homeScore += currentPA.runs
			
			if self.inning >= 9 and self.homeScore > self.awayScore:
			
				return False
			
			batter = self.homeTeam.lineup.newBatter()
			pitcher = self.awayTeam.lineup.currentPitcher
			
			return PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, currentPA.endState, batter, pitcher)
			
	def playInning(self):
		
		if self.inning >= 10 and self.top:
		
			if self.awayScore > self.homeScore:
			
				self.complete = True
				return True
		
		if self.inning == 9 and not self.top:
		
			if self.homeScore > self.awayScore:
			
				self.complete = True
				return True
		
		if self.top:
			
			if self.inning >= 6 and self.homeTeam.lineup.currentPitcher.pitchingGameStats['WPA'] < 0 and random.randint(0,100) > 50:
				
				self.homeTeam.lineup.subPitcher()
				
			batter = self.awayTeam.lineup.newBatter()
			pitcher = self.homeTeam.lineup.currentPitcher
		
		elif not self.top:
			
			if self.inning >=6 and self.awayTeam.lineup.currentPitcher.pitchingGameStats['WPA'] < 0 and random.randint(0,100) > 50:
			
				self.awayTeam.lineup.subPitcher()
				
			batter = self.homeTeam.lineup.newBatter()
			pitcher = self.awayTeam.lineup.currentPitcher
		
		currentPA = PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, BaseOutState(), batter, pitcher)
		
		while True:
		
			currentPA = self.iterate(currentPA)
			
			if not currentPA:
			
					self.complete = True
					return True
			
			if currentPA.endState.outs == 3:
				
				self.PAs.append(currentPA)
				
				if not self.top:
					self.inning += 1
					self.top = not self.top
					
				elif self.top:
					self.top = not self.top
					
				return True
				
	def play(self):
		
		while not self.complete:
			self.playInning()
	
	def tearDown(self):
	
		for player in self.homeTeam.lineup.battingOrder:
			player.save()
			
		for player in self.awayTeam.lineup.battingOrder:
			player.save()
			
		for player in self.homeTeam.lineup.usedPitchers:
			player.save()
			
		for player in self.awayTeam.lineup.usedPitchers:
			player.save()
			
		return True
	
	def gameLog(self):
	
		for i in self.PAs:
		
			print('Top ' if i.top else 'Bot ', i.inning, " | ", i)
			
		return True