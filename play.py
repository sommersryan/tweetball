import random, datetime
from utils import baseNarratives, transitions

class Event(object):

	def __init__(self):
	
		self.type = ''
		self.batterOut = False
		self.outs = 0
		
	@classmethod
	def fromString(cls):
	
		pass

class BaseOutState(object):

	def __init__(self, first=None, second=None, third=None, outs=0):
	
		self.first = first
		self.second = second
		self.third = third
		self.outs = outs
		
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
	
		return [self.third, self.second, self.first]
		
class PlateAppearance(object):
	
	def __init__(self, inning, baseState, batter, pitcher):
		
		self.inning = inning
		self.baseState = baseState
		self.batter = batter
		self.pitcher = pitcher
		self.transitions = transitions[baseState.getState()]
		self.event = None
		
	def advanceRunners(self, newBases, runs):
		
		oldState = self.baseState
		newState = BaseOutState()
		runners = oldState.queue()
		
		for i in range(0, runs):
			
			runners.pop()
		
		if len(runners) > 0:
		
			if '3' in str(newBases):
			
				newState.third = runners.pop()
				
		if len(runners) > 0:
		
			if '2' in str(newBases):
			
				newState.second = runners.pop()
				
		if len(runners) > 0:
		
			if '1' in str(newBases):
			
				newState.first = runners.pop()	
				
		if not self.event.batterOut:
		
			newState.first = self.batter
			
		return newState

class Game(object):

	def __init__(self):
	
		self.homeTeam = None
		self.awayTeam = None
		self.homeScore = 0
		self.awayScore = 0
		self.PAs = []
		self.inning = 1
		self.half = 'top'
		self.startTime = datetime.datetime.now()
		self.complete = False
		