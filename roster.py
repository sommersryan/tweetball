import random
from league import BAT_DIST, PITCH_DIST
from utils import percentile
from config import RESULT_TYPES

class Ratings(object):

	def __init__(self):
		
		self.contact = random.randint(1,99)
		self.power = random.randint(1,99)
		self.discipline = random.randint(1,99)
		self.control = random.randint(1,99)
		self.stuff = random.randint(1,99)
		self.composure = random.randint(1,99)
		
		self.batting = {}
		self.pitching = {}
		
		self.batting['single'] = percentile(self.contact, BAT_DIST['single'])
		self.batting['strikeout'] = percentile((100-self.contact), BAT_DIST['strikeout'])
		self.batting['double'] = percentile(self.power, BAT_DIST['double'])
		self.batting['triple'] = percentile(self.power, BAT_DIST['triple'])
		self.batting['HR'] = percentile(self.power, BAT_DIST['HR'])
		self.batting['inPlayOut'] = percentile((100-self.power), BAT_DIST['inPlayOut'])
		self.batting['BB'] = percentile(self.discipline, BAT_DIST['BB'])
		self.batting['HBP'] = percentile(self.discipline, BAT_DIST['HBP'])
		self.batting['sacrifice'] = percentile(random.randint(1,99),BAT_DIST['sacrifice'])
		self.batting['GDP'] = percentile(random.randint(1,99),BAT_DIST['GDP'])
		self.batting['error'] = percentile(random.randint(1,99),BAT_DIST['error'])
		
		self.pitching['single'] = percentile((100-self.stuff), PITCH_DIST['single'])
		self.pitching['strikeout'] = percentile(self.stuff, PITCH_DIST['strikeout'])
		self.pitching['double'] = percentile((100-self.control), PITCH_DIST['double'])
		self.pitching['triple'] = percentile((100-self.control), PITCH_DIST['triple'])
		self.pitching['HR'] = percentile((100-self.control), PITCH_DIST['HR'])
		self.pitching['inPlayOut'] = percentile(self.stuff, PITCH_DIST['inPlayOut'])
		self.pitching['BB'] = percentile((100-self.control), PITCH_DIST['BB'])
		self.pitching['HBP'] = percentile((100-self.control), PITCH_DIST['HBP'])
		self.pitching['sacrifice'] = percentile(random.randint(1,99), PITCH_DIST['sacrifice'])
		self.pitching['GDP'] = percentile(self.composure, PITCH_DIST['GDP'])
		self.pitching['error'] = percentile(random.randint(1,99), PITCH_DIST['error'])
			
			
class Player(object):

	def __init__(self, twitterUser):
		#twitterUser is a tweepy user object
		self.id = twitterUser['id']
		self.name = twitterUser['screenname']
		self.handedness = random.choice(['L','R','S'])
		self.uniNumber = random.randint(0,71)
		self.ratings = Ratings()
		
	@classmethod
	def fake(cls):
	
		id = random.randint(111111,999999)
		user = 'Player{0}'.format(random.randint(1,1000))
		twitterUser = {'id' : id, 'screenname' : user }
		inst = cls(twitterUser)
		
		return inst
		
class Lineup(object):

	def __init__(self, battingOrder, pitchers):
	
		self.battingOrder = battingOrder
		self.pitchers = pitchers
		self.currentPitcher = pitchers[0]
		self.atBat = 0
		self.onDeck = 1
		
	def random(self):
		#load 9 random players and 3 or so pitchers from S3
		pass
	
	@classmethod
	def dummy(cls):
		
		bOrder = []
		pitchers = []
		
		for i in range(0,9):
			bOrder.append(Player.fake())
			
		for i in range(0,4):
			pitchers.append(Player.fake())
			
		inst = cls(bOrder, pitchers)
		
		return inst
		
	def newBatter(self):
		
		nb = self.battingOrder[self.onDeck]
		
		if self.onDeck == 8:
			self.onDeck = 0	
		
		else:
			self.onDeck += 1
			
		return nb

	def assignPositions(self):
		pass
		
class Team(object):

	def __init__(self, nickname, location, lineup):
	
		self.nickname = nickname
		self.location = location
		self.lineup = lineup
	
	@classmethod
	def dummy(cls):
	
		nickname = "{0}ers".format(random.randint(0,100))
		location = "Place{0}".format(random.randint(0,100))
		lineup = Lineup.dummy()
		
		inst = cls(nickname, location, lineup)
		
		return inst
		
	def __str__(self):
	
		return "{0} {1}".format(self.location, self.nickname)
