import random, datetime

class PlateAppearance(object):
	
	def __init__(self, inning, startOuts, baseState, batter, pitcher):
		
		self.inning = inning
		self.startOuts = startOuts
		self.baseState = baseState
		self.batter = batter
		self.pitcher = pitcher
		self.pitches = []
	
	def throwPitch(self):
	
		pass
		
class Event(object):
	
	def __init__(self, plateAppearance):
	
		pass

class BallInPlay(Event):
	
	def __init__(self, plateAppearance):
		Event.__init__(self, plateAppearance)
		
class Player(object):

	def __init__(self, twitterUser):
		#twitterUser is a tweepy user object. initialize some basic stuff here
		self.id = twitterUser['id']
		self.handedness = random.choice(['L','R'])
		self.uniNumber = random.randint(0,71)
		
class Batter(Player):

	def __init__(self, twitterUser):
		Player.__init__(self, twitterUser)
		self.position = None
		self.switchHitter = False
		
class Pitcher(Player):
	
	def __init__(self, twitterUser):
		Player.__init__(self, twitterUser)
		self.repertoire = []
		
class Lineup(object):

	def __init__(self, team):
	
		self.battingOrder = []
		self.pitchers = []
		self.team = team 
		
	def makeLineup(self):
	
		pass
		
	def assignPositions(self):

		pass
		
class Team(object):

	def __init__(self):
	
		self.nickname = None
		self.location = None
		self.stadium = None
		
	def __str__(self):
	
		return "{0} {1}".format(self.location, self.nickname)

class Game(object):

	def __init__(self):
	
		self.homeTeam = None
		self.awayTema = None
		self.startTime = datetime.datetime.now()
		self.complete = False
		
class BaseState(object):

	def __init__(self):
	
		self.onFirst = None
		self.onSecond = None
		self.onThird = None
		
	#advanceOn methods for each play type to properly advance runners?
	#or one advance method to handle multiple event types