import random, datetime

class PlateAppearance(object):
	
	def __init__(self, inning, baseState, batter, pitcher):
		
		self.inning = inning
		self.baseState = baseState
		self.batter = batter
		self.pitcher = pitcher
	
class Game(object):

	def __init__(self):
	
		self.homeTeam = None
		self.awayTema = None
		self.startTime = datetime.datetime.now()
		self.complete = False
		
class BaseOutState(object):

	def __init__(self):
	
		self.first = None
		self.second = None
		self.third = None