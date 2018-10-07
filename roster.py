import random
from league import BAT_DIST, PITCH_DIST
from utils import percentile, nicknames, getCity
from config import RESULT_TYPES
from tweet import api
from collections import deque
from pymongo import MongoClient
from config import MONGO_URI, CURRENT_SEASON
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client.tweetball
playerColl = db.players
teamColl = db.teams

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

	# The Player class essentially acts as an interface for the players collection in mongoDB. 
	# The class itself stores only the mongo ObjectID, and uses that to get and set attributes directly
	# in the database, as well as increment stats and update the database with changes to the user's3
	# twitter profile. 
	
	def __init__(self, objectID):
		
		# Initializes with a objectID of an existing record, pulls record and stores reference to mongo objectID
		
		self.ref = objectID
		self.spent = False # True for pitchers or hitters who have been subbed out
		self.sub = False
		self.position = None
		
	def __getattr__(self, key):
	
		# Exposes elements of the db document as properties of the object
		
		return playerColl.find_one({'_id' : self.ref})[key]
		
	def __setattr__(self, key, value):
		
		# so init doesn't cause recursion:
		
		if key == 'ref':
			self.__dict__['ref'] = value
		
		else:
			playerColl.update({'_id' : self.ref}, { "$set" : { key : value }})
		
	def increment(self, side, stat, amount = 1, season = CURRENT_SEASON):
		
		# Increments a specified stat by a specified amount 
		# Side parameter must be 'batting' or 'pitching'
		
		if side not in ['batting', 'pitching']:
			raise KeyError
		
		keyString = "stats.seasons.{0}.{1}.{2}".format(season, side, stat)
		playerColl.update( { "_id" : self.ref }, { "$inc" : { keyString : amount }} )
		
		return True

	@staticmethod
	def new(twitterUser):
	
		# Adds a new document to the  player database based on a passed tweepy user object
		
		# Build a dict to insert, first with basic attributes from the tweepy user
		
		doc = {
				'id' : twitterUser.id,
				'name' : twitterUser.screen_name,
				'fullName' : twitterUser.name,
				'handle' : "@{0}".format(twitterUser.screen_name),
				'handedness' : random.choice(['L','R','S']),
				'uniNumber' : random.randint(0,71),
				'avatarURL' : twitterUser.profile_image_url_https,
				'headerURL' : twitterUser.profile_banner_url}
		
		# Generate some ratings, and then add them in the appropriate keys
		
		ratings = Ratings()
		
		doc['ratings'] = {}
		doc['probabilities'] = {}
		doc['probabilities']['batting'] = ratings.__dict__.pop('batting')
		doc['probabilities']['pitching'] = ratings.__dict__.pop('pitching')
		doc['ratings'].update(ratings.__dict__)
		
		doc['lastStart'] = datetime.utcnow()
		
		# Insert the completed doc into the collection
		
		playerColl.insert(doc)
		
		return True
	
	@staticmethod
	def refresh(player):
	
		twitterUser = api.get_user(player.id)
		
		updates = {
					'name' : twitterUser.screen_name,
					'fullName' : twitterUser.name,
					'handle' : "@{0}".format(twitterUser.screen_name),
					'avatarURL' : twitterUser.profile_image_url_https,
					'headerURL' : twitterUser.profile_banner_url
					}
		
		new = api.get_user(self.id)
		self.id = new.id
		self.name = new.screen_name
		self.handle = "@{0}".format(new.screen_name)
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
								self.ratings['contact'],
								self.ratings['power'],
								self.ratings['discipline'],
								self.ratings['control'],
								self.ratings['stuff'],
								self.ratings['composure'])
		
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
		p = pickle.loads(raw)
		return p
		
class Lineup(object):

	def __init__(self, objectID):
		
		self.ref = objectID
		self.nickname = teamColl.find_one({'_id' : self.ref})['nickname']
		self.location = teamColl.find_one({'_id' : self.ref})['city']
		
		self.batters = deque([Player(p) for p in teamColl.find_one({'_id' : self.ref})['batters']])
		
		# Sort the pitcher list from the db by earliest date of last start, convert to deque for popleft
		pitcherList = [Player(p) for p in teamColl.find_one({'_id' : self.ref})['pitchers']]
		pitcherList.sort(key = lambda x: x.lastStart)
		self.pitchers = deque(pitcherList)
		
		# Some properties for handling a batting lineup
		self.lineup = []
		self.onDeck = 1
		self.atBat = 0
		
		self.currentPitcher = None
		
		# Runs for the game to track
		self.runs = 0
		
	def makeLineup(self):
		
		# Adds eight random players to the team's lineup and assigns them positions
		
		random.shuffle(self.batters)
		
		for i in range(0,8):
			self.lineup.append(self.batters.popleft())
	
		positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
		random.shuffle(positions)
		
		for b in self.lineup:
			b.position = positions.pop()
		
		return True
		
	def getStarter(self):
		
		# Selects the pitcher who has pitched least recently and makes him starter, adds to lineup
		
		self.currentPitcher = self.pitchers.popleft()
		self.currentPitcher.position = 'SP'
		self.lineup.append(self.currentPitcher)
		
		return True
		
	def newBatter(self):
		
		isSpent = True
		
		while isSpent:	
		
			try:
				nb = self.lineup[self.onDeck]
				self.atBat = self.onDeck
				self.onDeck += 1
		
			except IndexError:
				nb = self.lineup[0]
				self.atBat = 0
				self.onDeck = 1
			
			isSpent = nb.spent
			
		return nb
		
	def pitchingChange(self):
		
		# Changes out the pitcher for the next one in the queue
		# This method removes the used pitcher from the pitchers list
		
		try:
		
			newPitcher = self.pitchers.popleft()
			
			self.currentPitcher.spent = True
			newPitcher.position = 'RP'
			newPitcher.sub = True
			
			self.lineup.insert(self.lineup.index(self.currentPitcher) + 1, newPitcher)
			self.currentPitcher = newPitcher
			
			return True
			
		except IndexError:
			# Popping from empty list means no more pitchers left in the pen; do nothing
			return True
		

	def pinchHitter(self, pinchFor):
	
		# Changes out batter (Player pinchFor) for a substitute.
		
		try:
		
			newBatter = self.batters.popleft()
			newBatter.position = pinchFor.position
			newBatter.sub = True
			
			pinchFor.spent = True
			
			self.lineup.insert(self.lineup.index(pinchFor) + 1, newBatter)
			
			return True
		
		except IndexError:
			# Popping from empty list means no more batters; do nothing
			return True
	
	def __str__(self):
	
		return "{0} {1}".format(self.location, self.nickname)

def getTeams():

	keys = list(playerStore.list())
	players = [Player.load(a) for a in keys]
	playersSorted = sorted(players, key = lambda x: x.battingCareerStats['PA'])
	paGroups = []
	
	for k, g in groupby(playersSorted, key=lambda x: x.battingCareerStats['PA']):
		paGroups.append(list(g))
		
	finalPool = paGroups[0]
	
	for i in paGroups[1:]:
		if len(finalPool) < 24:
			finalPool += i
		else:
			break
	
	random.shuffle(finalPool)
	pool = finalPool[:24]
	
	for p in pool:
		p.refresh()
	
	pool.sort(key = lambda x: (x.ratings.control + x.ratings.stuff), reverse = False)
	homeHitters, homePitchers, awayHitters, awayPitchers = [], [], [], []
	
	for i in range(0,9):
		homeHitters.append(pool.pop())
		awayHitters.append(pool.pop())
		
	for i in range(0,3):
		homePitchers.append(pool.pop())
		awayPitchers.append(pool.pop())

	homeLoc = getCity()
	awayLoc = getCity()
	homeNick = random.choice(nicknames)
	awayNick = random.choice(nicknames)
	
	homeLineup = Lineup(homeHitters, homePitchers)
	awayLineup = Lineup(awayHitters, awayPitchers)
	
	homeTeam = Team(homeNick, homeLoc, homeLineup)
	awayTeam = Team(awayNick, awayLoc, awayLineup)
	
	return(homeTeam, awayTeam)