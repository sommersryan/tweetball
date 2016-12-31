import random
from league import AVG_OUTCOMES


class Ratings(object):
	
	#Hitters: 
	#	CON - more singles, less strikeouts
	#   POW - more extra base hits, less inPlayOuts
	#   DIS - more walks, less strikeouts
	#
	#Pitchers:
	#	CTR - less walks, more inPlayOuts
	#	STF - more strikeouts, less extra base hits
	#	CMP - more GDP, less extra base hits 
	
	def __init__(self):
		
		self.contact = random.triangular(0,100,60)
		self.power = random.triangular(0,100,60)
		self.discipline = random.triangular(0,100,60)
		self.control = random.triangular(0,100,60)
		self.stuff = random.triangular(0,100,60)
		self.composure = random.triangular(0,100,60)
		
		attributes = AVG_OUTCOMES
		
		
		
	
		
class Player(object):

	def __init__(self, twitterUser):
		#twitterUser is a tweepy user object. initialize some basic stuff here
		self.id = twitterUser['id']
		self.handedness = random.choice(['L','R','S'])
		self.uniNumber = random.randint(0,71)
		
class Batter(Player):

	def __init__(self, twitterUser):
		super().__init__(self, twitterUser)
		self.attributes = Hitting.random()
		
class Pitcher(Player):
	
	def __init__(self, twitterUser):
		super().__init__(self, twitterUser)
		
class Lineup(object):

	def __init__(self, team):
	
		self.battingOrder = []
		self.pitchers = []
		self.team = team 
		
	def random(self):
		#load 9 random players and 3 or so pitchers from S3
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
