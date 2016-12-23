import random

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
