import random, pickle, forgery_py
from league import BAT_DIST, PITCH_DIST
from utils import percentile, nicknames
from config import RESULT_TYPES
from tweet import api
from storage import playerStore
from collections import Counter
from boto.s3.key import Key

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
		self.id = twitterUser.id
		self.name = twitterUser.screen_name
		self.fullName = twitterUser.name
		self.handle = "@{0}".format(twitterUser.screen_name)
		self.handedness = random.choice(['L','R','S'])
		self.uniNumber = random.randint(0,71)
		self.ratings = Ratings()
		self.pitchingGameStats = Counter()
		self.battingGameStats = Counter()
		self.pitchingCareerStats = Counter()
		self.battingCareerStats = Counter()
		self.active = True
		self.sub = False
		self.position = None

	def save(self):
	
		k = Key(playerStore)
		k.key = self.id
		zipped = pickle.dumps(self)
		k.set_contents_from_string(zipped)
		
		return True
		
	def refresh(self):
		
		new = api.get_user(self.id)
		self.id = new.id
		self.name = "@{0}".format(new.screen_name)
		self.fullName = new.name
		
		return True
	
	def notifyAttributes(self):
	
		attrTweet = """{0}\r\n
					HITTING:\r\n
					Contact: {1}\r\nPower: {2}\r\nDiscipline: {3}\r\n
					\r\n
					PITCHING:\r\n
					Control: {4}\r\nStuff: {5}\r\nComposure: {6}
					""".format(self.handle,
								self.ratings.contact,
								self.ratings.power,
								self.ratings.discipline,
								self.ratings.control,
								self.ratings.stuff,
								self.ratings.composure)
		
		api.update_status(attrTweet)
		return True
		
	def __repr__(self):
	
		return "<Player {0}>".format(self.name)
	
	def __str__(self):
	
		return self.handle
		
	@staticmethod
	def load(playerID):
	
		k = playerStore.get_key(playerID)
		raw = k.get_contents_as_string()
		return pickle.loads(raw)
		
class Lineup(object):

	def __init__(self, battingOrder, pitchers):
	
		self.battingOrder = battingOrder
		self.pitchers = pitchers
		self.pitchers.insert(0, random.choice(battingOrder))
		self.currentPitcher = pitchers.pop(0)
		self.usedPitchers = [self.currentPitcher,]
		self.atBat = 0
		self.onDeck = 1
		self.assignPositions()
		
	def newBatter(self):
		
		isActive = False
		
		while not isActive:
		
			try:
				nb = self.battingOrder[self.onDeck]
				self.onDeck += 1
		
			except IndexError:
				nb = self.battingOrder[0]
				self.onDeck = 1
			
			isActive = nb.active
			
		return nb

	def assignPositions(self):
		
		positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
		random.shuffle(positions)
		
		for player in self.battingOrder:
			
			if player == self.currentPitcher:
				player.position = 'P'
				
			else:
				player.position = positions.pop()
		
		return True
		
	def subPitcher(self):
	
		if self.pitchers:
		
			self.currentPitcher.active = False
			substitute = self.pitchers.pop(0)
			substitute.sub = True
			substitute.position = 'P'
			self.battingOrder.insert(self.battingOrder.index(self.currentPitcher) + 1, substitute)
			self.currentPitcher = substitute
			self.usedPitchers += [self.currentPitcher]
		
class Team(object):

	def __init__(self, nickname, location, lineup):
	
		self.nickname = nickname
		self.location = location
		self.lineup = lineup
	
	def __str__(self):
	
		return "{0} {1}".format(self.location, self.nickname)

def getTeams():

	keys = list(playerStore.list())
	pool = random.sample(keys,24)
	homeHitters, homePitchers, awayHitters, awayPitchers = [], [], [], []
	
	for i in range(0,9):
		homeHitters.append(Player.load(pool.pop().key))
		awayHitters.append(Player.load(pool.pop().key))
		
	for i in range(0,3):
		homePitchers.append(Player.load(pool.pop().key))
		awayPitchers.append(Player.load(pool.pop().key))
		
	homeLoc = forgery_py.address.city()
	awayLoc = forgery_py.address.city()
	homeNick = random.choice(nicknames)
	awayNick = random.choice(nicknames)
	
	homeLineup = Lineup(homeHitters, homePitchers)
	awayLineup = Lineup(awayHitters, awayPitchers)
	
	homeTeam = Team(homeNick, homeLoc, homeLineup)
	awayTeam = Team(awayNick, awayLoc, awayLineup)
	
	return(homeTeam, awayTeam)