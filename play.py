import random, datetime, config
from config import AD_RATES
from utils import baseNarratives, transitions, log5, weightedChoice, emojis
from league import leagueMeans
from tweet import api
from wpa import winProb
from fractions import Fraction

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
				 'homers' : self.homer
				 'walks' : self.walk
				 'strikes out' : self.strikeout
				 'flies out' : self.flyout
				 'lines out': self.lineout
				 'grounds out': self.groundout
				 'is hit by pitch' : self.hbp
				 'error' : self.error
				 'steals' : self.steal
				 'enters to pitch' : self.bullpenCall
				 'enters as a pinch hitter' : self.pinchHitter
				} 
		
		self.top = kwargs.pop('top')
		self.inning = kwargs.pop('inning')
		self.pitcher = kwargs.pop('pitcher')
		self.beginState = kwargs.pop('beginState')
		self.battingTeam = kwargs.pop('battingTeam')
		self.pitchingTeam = kwargs.pop('pitchingTeam')
		self.type = kwargs.pop('type')
		self.func = funcs['self.type']
		self.endState = self.func()['endState']
		self.runs = self.func()['runs']
		
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
					
class BaseOutState(object):

	def __init__(self, battingLineup, batter, first=None, second=None, third=None, outs=0, runs=0):
	
		"""
		A BaseOutState object contains Player objects for every player 
		on base and at the plate, as well as an integer representing the
		number of outs, and the batting team's number of runs and lineup object. 
		The advance() class method instantiates a new BaseOutState based on the event 
		object ('single', 'double', etc) passed to it. The singledispatch decorator 
		is used to allow the advance method to accept any type of event and return 
		the correct new state.
		"""
	
		self.batter = batter
		self.first = first
		self.second = second
		self.third = third
		self.outs = outs
		self.runs = runs
		self.battingLineup = battingLineup
		
		# forced is a list containing any runners who are forced by the runners behind
		# them to advance
		
		self.forced = [self.first]
		
		if self.first:
			self.forced.append(self.second)
			
		if self.second and self.first:
			self.forced.append(self.third)
		
	@classmethod
	def strikeout(cls, state):
		
		"""
		This and subsequent class methods advance runners from the passed state
		based on the named event, and instantiates a new base state. 
		"""
		
		first, second, third = state.first, state.second, state.third
		battingLineup = state.battingLineup
		outs = state.outs + 1
		runs = state.runs
		
		if outs < 3:
			batter = state.battingLineup.newBatter()
		else:
			batter = None
		
		inst = cls(battingLineup, batter, first, second, third, outs, runs)
		
		return inst
		
	@classmethod
	def walk(cls, state):
		
		outs = state.outs
		first = state.batter
		batter = state.battingLineup.newBatter()
		
		if state.third and state.third in state.forced:
			runs = state.runs + 1
			third = state.second
			second = state.first
			
	
	def getState(self):
		
		firstBase, secondBase, thirdBase = '', '', ''
		
		if self.first:
			firstBase = '1'
			
		if self.second:
			secondBase = '2'
			
		if self.third:
			thirdBase = '3'
			
		state = '{0}{1}{2}'.format(firstBase, secondBase, thirdBase)
		
		if state == '':
			state = '0'
		
		return (int(state), self.outs)
			
	def __str__(self):
		
		narr = baseNarratives[self.getState()[0]]
		
		return "{0} and {1} outs".format(narr, self.outs)
	
	def queue(self):
	
		runners = []
		
		for runner in [self.first, self.second, self.third]:
		
			if runner:
			
				runners.append(runner)
				
		return runners
		
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
		self.runs = kwargs.pop('runs')
		
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