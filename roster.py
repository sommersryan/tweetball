import random
from league import BAT_DIST, PITCH_DIST
from utils import percentile


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
		
		self.contact = random.randint(1,100)
		self.power = random.randint(1,100)
		self.discipline = random.randint(1,100)
		self.control = random.randint(1,100)
		self.stuff = random.randint(1,100)
		self.composure = random.randint(1,100)
		
		self.batting = {}
		self.pitching = {}
		
		self.batting['single'] = percentile(self.contact, BAT_DIST['single'])
		self.batting['strikeout'] = percentile((100-self.contact), BAT_DIST['strikeout'])
		self.batting['double'] = percentile(self.power, BAT_DIST['double'])
		self.batting['triple'] = percentile(self.power, BAT_DIST['triple'])
		self.batting['HR'] = percentile(self.power, BAT_DIST['HR'])
		self.batting['inPlayOut'] = percentile((100-self.power), BAT_DIST['inPlayOut'])
		self.batting['BB'] = percentile(self.discipline, BAT_DIST['BB'])
		self.batting['sacrifice'] = percentile(random.randint(1,100),BAT_DIST['sacrifice'])
		self.batting['GDP'] = percentile(random.randint(1,100),BAT_DIST['GDP'])
		self.batting['error'] = percentile(random.randint(1,100),BAT_DIST['error'])
		
		self.pitching['single'] = percentile((100-self.stuff), PITCH_DIST['single'])
		self.pitching['strikeout'] = percentile(self.stuff, PITCH_DIST['strikeout'])
		self.pitching['double'] = percentile((100-self.control), PITCH_DIST['double'])
		self.pitching['triple'] = percentile((100-self.control), PITCH_DIST['triple'])
		self.pitching['HR'] = percentile((100-self.control), PITCH_DIST['HR'])
		self.pitching['inPlayOut'] = percentile(self.stuff, PITCH_DIST['inPlayOut'])
		self.pitching['BB'] = percentile(self.control, PITCH_DIST['BB'])
		self.pitching['sacrifice'] = percentile(random.randint(1,100), PITCH_DIST['sacrifice'])
		self.pitching['GDP'] = percentile(self.composure, PITCH_DIST['GDP'])
		self.pitching['error'] = percentile(random.randint(1,100), PITCH_DIST['error'])
			
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
