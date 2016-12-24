import random
from attributes import Hitting, Pitching

class Player(object):

	def __init__(self, twitterUser):
		#twitterUser is a tweepy user object. initialize some basic stuff here
		self.id = twitterUser['id']
		self.handedness = random.choice(['L','R','S'])
		self.uniNumber = random.randint(0,71)
		
class Batter(Player):

	def __init__(self, twitterUser):
		Player.__init__(self, twitterUser)
		self.position = random.choice('C','1B','2B','3B', 'LF', 'CF', 'RF')
		self.attributes = Hitting.random()
		
		
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
