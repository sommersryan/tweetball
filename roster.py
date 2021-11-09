import random, pickle
from league import BAT_DIST, PITCH_DIST
from utils import percentile, nicknames, getCity
from config import RESULT_TYPES, PLAYER_SAVING_ENABLED
# from tweet import api
from tweepy.error import TweepError
from storage import playerStore
from fractions import Fraction
from collections import Counter
from datetime import datetime
from itertools import groupby
from boto.s3.key import Key
from mongo_player_store import mongoPlayerSave, mongoGetPlayersByLastStartAscending, mongoMapToPlayer, playerMaptoMongo

class Ratings(object):
	
	def __init__(self, contact, power, discipline, control, stuff, 
	composure, batting, pitching):
	
		self.contact = contact
		self.power = power
		self.discipline = discipline
		self.control = control
		self.stuff = stuff
		self.composure = composure
		self.batting = batting
		self.pitching = pitching
	
	@classmethod
	def new(cls):
		
		contact = random.randint(1,99)
		power = random.randint(1,99)
		discipline = random.randint(1,99)
		control = random.randint(1,99)
		stuff = random.randint(1,99)
		composure = random.randint(1,99)
		
		batting = {}
		pitching = {}
		
		batting['single'] = percentile(contact, BAT_DIST['single'])
		batting['strikeout'] = percentile((100-contact), BAT_DIST['strikeout'])
		batting['double'] = percentile(power, BAT_DIST['double'])
		batting['triple'] = percentile(power, BAT_DIST['triple'])
		batting['HR'] = percentile(power, BAT_DIST['HR'])
		batting['inPlayOut'] = percentile((100-power), BAT_DIST['inPlayOut'])
		batting['BB'] = percentile(discipline, BAT_DIST['BB'])
		batting['HBP'] = percentile(discipline, BAT_DIST['HBP'])
		batting['sacrifice'] = percentile(random.randint(1,99),BAT_DIST['sacrifice'])
		batting['GDP'] = percentile(random.randint(1,99),BAT_DIST['GDP'])
		batting['error'] = percentile(random.randint(1,99),BAT_DIST['error'])
		
		pitching['single'] = percentile((100-stuff), PITCH_DIST['single'])
		pitching['strikeout'] = percentile(stuff, PITCH_DIST['strikeout'])
		pitching['double'] = percentile((100-control), PITCH_DIST['double'])
		pitching['triple'] = percentile((100-control), PITCH_DIST['triple'])
		pitching['HR'] = percentile((100-control), PITCH_DIST['HR'])
		pitching['inPlayOut'] = percentile(stuff, PITCH_DIST['inPlayOut'])
		pitching['BB'] = percentile((100-control), PITCH_DIST['BB'])
		pitching['HBP'] = percentile((100-control), PITCH_DIST['HBP'])
		pitching['sacrifice'] = percentile(random.randint(1,99), PITCH_DIST['sacrifice'])
		pitching['GDP'] = percentile(composure, PITCH_DIST['GDP'])
		pitching['error'] = percentile(random.randint(1,99), PITCH_DIST['error'])
		
		ratingSet = cls(contact, power, discipline, control, stuff, composure,
		batting, pitching)
		
		return ratingSet
	
	@classmethod
	def blank(cls):
		contact = 0
		power = 0
		discipline = 0
		control = 0
		stuff = 0
		composure = 0
		
		batting = {}
		pitching = {}
		
		ratingSet = cls(contact, power, discipline, control, stuff, composure,
		batting, pitching)
		
		return ratingSet
			
class Player(object):

	def __init__(self, id, name, fullName, handle, handedness,
	uniNumber, ratings, pitchingGameStats, battingGameStats, 
	pitchingCareerStats, battingCareerStats, active, sub, position):
		
		self.id = id
		self.name = name
		self.fullName = fullName
		self.handle = handle
		self.handedness = handedness
		self.uniNumber = uniNumber
		self.ratings = ratings
		self.pitchingGameStats = pitchingGameStats
		self.battingGameStats = battingGameStats
		self.pitchingCareerStats = pitchingCareerStats
		self.battingCareerStats = battingCareerStats
		self.active = active
		self.sub = sub
		self.position = position
	
	@classmethod
	def fromTwitter(cls, twitterUser):
		#twitterUser is a tweepy user object
		
		id = twitterUser.id
		name = twitterUser.screen_name
		fullName = twitterUser.name
		handle = "@{0}".format(twitterUser.screen_name)
		handedness = random.choice(['L','R','S'])
		uniNumber = random.randint(0,71)
		ratings = Ratings.new()
		pitchingGameStats = Counter()
		battingGameStats = Counter()
		pitchingCareerStats = Counter()
		battingCareerStats = Counter()
		active = True
		sub = False
		position = None
		
		pitchingCareerStats['IP'] = Fraction(0, 1)
		
		player = cls(id, name, fullName, handle, handedness, uniNumber,
		ratings, pitchingGameStats, battingGameStats, pitchingCareerStats,
		battingCareerStats, active, sub, position)
		
		return player

	def save(self):
		
		self.pitchingCareerStats.update(self.pitchingGameStats)
		self.battingCareerStats.update(self.battingGameStats)
		
		record = playerMaptoMongo(self)
		
		if self.position == "P":
			if self.pitchingGameStats['IP'] >= 2:
				record['lastStart'] = datetime.utcnow()
				
		else:
			record['lastStart'] = datetime.utcnow()
		
		if PLAYER_SAVING_ENABLED:
			mongoPlayerSave(record)
		
		return True
		
	# def refresh(self):
	#
	# 	try:
	# 		#new = api.get_user(self.id)
	#
	# 	except TweepError:
	# 		return False
	#
	# 	self.id = new.id
	# 	self.name = new.screen_name
	# 	self.handle = "@{0}".format(new.screen_name)
	# 	self.fullName = new.name
	#
	# 	return True
	
	# def notifyAttributes(self):
	#
	# 	attrTweet = """{0}\r\n
	# 				HITTING:\r\n
	# 				Contact: {1}\r\nPower: {2}\r\nDiscipline: {3}\r\n
	# 				\r\n
	# 				PITCHING:\r\n
	# 				Control: {4}\r\nStuff: {5}\r\nComposure: {6}
	# 				""".format(self.handle,
	# 							self.ratings.contact,
	# 							self.ratings.power,
	# 							self.ratings.discipline,
	# 							self.ratings.control,
	# 							self.ratings.stuff,
	# 							self.ratings.composure)
	#
	# 	api.update_status(attrTweet)
	# 	return True
		
	def __repr__(self):
	
		return "<Player {0}>".format(self.name)
	
	def __str__(self):
	
		return self.handle
	
	@classmethod
	def blank(cls):
		id = ''
		name = ''
		fullName = ''
		handle = ''
		handedness = ''
		uniNumber = 0
		ratings = Ratings.blank()
		pitchingGameStats = Counter()
		battingGameStats = Counter()
		pitchingCareerStats = Counter()
		battingCareerStats = Counter()
		active = True
		sub = False
		position = None
		
		player = cls(id, name, fullName, handle, handedness, uniNumber,
		ratings, pitchingGameStats, battingGameStats, pitchingCareerStats,
		battingCareerStats, active, sub, position)
		
		return player
	
	@staticmethod
	def load(playerID):
	
		k = playerStore.get_key(playerID)
		raw = k.get_contents_as_string()
		p = pickle.loads(raw) 
		return p
		
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
		
	def subPitcher(self, previousPA):
	
		if self.pitchers:
		
			self.currentPitcher.active = False
			substitute = self.pitchers.pop(0)
			substitute.sub = True
			substitute.position = 'P'
			
			subInfo = Substitution(self.currentPitcher, substitute, previousPA, True)
			
			self.battingOrder.insert(self.battingOrder.index(self.currentPitcher) + 1, substitute)
			self.currentPitcher = substitute
			self.usedPitchers += [self.currentPitcher]
			
			return subInfo
			
		return False
		
class Team(object):

	def __init__(self, nickname, location, lineup):
	
		self.nickname = nickname
		self.location = location
		self.lineup = lineup
	
	def __str__(self):
	
		return "{0} {1}".format(self.location, self.nickname)
		
class Substitution(object):

	def __init__(self, playerOut, playerIn, previousPA, isPitchingChange):
		
		self.top = previousPA.top
		self.inning = previousPA.inning
		self.outs = previousPA.endState.outs
		self.runs = 0
		self.isPitchingChange = isPitchingChange
		self.wpa = 0
		self.playerOut = playerOut
		self.playerIn = playerIn
		self.isSubstitution = True

		self.narratives = [str(self)]
		
	# def tweetPA(self, replyTo):
	#
	# 	if self.isPitchingChange:
	# 		tweet = "{0} enters the game to pitch, replacing {1}.".format(self.playerIn.handle, self.playerOut.handle)
	#
	# 	else:
	# 		tweet = "{0} enters the game to pinch hit for {1}.".format(self.playerIn.handle, self.playerOut.handle)
	#
	# 	tweetID = api.update_status(tweet, in_reply_to_status_id = replyTo).id
	#
	# 	return tweetID
		
	def __str__(self):
		
		if self.isPitchingChange:
			subString = "{0} enters the game to pitch, replacing {1}.".format(self.playerIn.handle, self.playerOut.handle)
			
		else:
			subString = "{0} enters the game to pinch hit for {1}.".format(self.playerIn.handle, self.playerOut.handle)
		
		return subString

def getTeams():

	mongoPlayers = mongoGetPlayersByLastStartAscending(24)
	
	pool = [mongoMapToPlayer(a, Player.blank()) for a in mongoPlayers]
	
	# for p in pool:
	# 	p.refresh()
	
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