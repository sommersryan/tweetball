import random, pickle
from game_engine.league import BAT_DIST, PITCH_DIST
from game_engine.utils import percentile, nicknames, getCity
from config import RESULT_TYPES, PLAYER_SAVING_ENABLED
from game_meta.tweet import api
from tweepy.error import TweepError
from fractions import Fraction
from collections import Counter
from datetime import datetime
from itertools import groupby
from boto.s3.key import Key
from mongo_player_store import mongoPlayerSave, mongoGetPlayersByLastStartAscending, mongoMapToPlayer, playerMaptoMongo

def generateRatings():

	ratings = {
				'contact' : random.randint(1,99),
				'power' : random.randint(1,99),
				'discipline' : random.randint(1,99),
				'control' : random.randint(1,99),
				'stuff' : random.randint(1,99),
				'composure' : random.randint(1,99)
			}
			
	return ratings
	
def rollProbabilities(ratingsDict):

	battingProbs = {}
	pitchingProbs = {}
	
	battingProbs['single'] = percentile(ratingsDict['contact'], BAT_DIST['single'])
	battingProbs['strikeout'] = percentile((100-ratingsDict['contact']), BAT_DIST['strikeout'])
	battingProbs['double'] = percentile(ratingsDict['power'], BAT_DIST['double'])
	battingProbs['triple'] = percentile(ratingsDict['power'], BAT_DIST['triple'])
	battingProbs['HR'] = percentile(ratingsDict['power'], BAT_DIST['HR'])
	battingProbs['inPlayOut'] = percentile((100-ratingsDict['power']), BAT_DIST['inPlayOut'])
	battingProbs['BB'] = percentile(ratingsDict['discipline'], BAT_DIST['BB'])
	battingProbs['HBP'] = percentile(ratingsDict['discipline'], BAT_DIST['HBP'])
	battingProbs['sacrifice'] = percentile(random.randint(1,99),BAT_DIST['sacrifice'])
	battingProbs['GDP'] = percentile(random.randint(1,99),BAT_DIST['GDP'])
	battingProbs['error'] = percentile(random.randint(1,99),BAT_DIST['error'])
	
	pitchingProbs['single'] = percentile((100-ratingsDict['stuff']), PITCH_DIST['single'])
	pitchingProbs['strikeout'] = percentile(ratingsDict['stuff'], PITCH_DIST['strikeout'])
	pitchingProbs['double'] = percentile((100-ratingsDict['control']), PITCH_DIST['double'])
	pitchingProbs['triple'] = percentile((100-ratingsDict['control']), PITCH_DIST['triple'])
	pitchingProbs['HR'] = percentile((100-ratingsDict['control']), PITCH_DIST['HR'])
	pitchingProbs['inPlayOut'] = percentile(ratingsDict['stuff'], PITCH_DIST['inPlayOut'])
	pitchingProbs['BB'] = percentile((100-ratingsDict['control']), PITCH_DIST['BB'])
	pitchingProbs['HBP'] = percentile((100-ratingsDict['control']), PITCH_DIST['HBP'])
	pitchingProbs['sacrifice'] = percentile(random.randint(1,99), PITCH_DIST['sacrifice'])
	pitchingProbs['GDP'] = percentile(ratingsDict['composure'], PITCH_DIST['GDP'])
	pitchingProbs['error'] = percentile(random.randint(1,99), PITCH_DIST['error'])
	
	probs = { 'batting' : battingProbs, 'pitching' : pitchingProbs }
	
	return probs
			
class Player(object):
	
	def __init__(self, **kwargs):
	
		self.active = True
		self.sub = False
	
		for key, value in kwargs.items():
		
			setattr(self, key, value)

	@classmethod
	def fromTwitter(cls, twitterUser):
		#twitterUser is a tweepy user object
		
		ratings = generateRatings()
		probs = rollProbabilities(ratings)
		
		kwargs = {
					'_id' : '',
					'id' : twitterUser.id,
					'name' : twitterUser.screen_name,
					'fullName' : twitterUser.name,
					'handle' : "@{0}".format(twitterUser.screen_name),
					'handedness' : random.choice(['L','R','S']),
					'uniNumber' : random.randint(0,71),
					'ratings' : ratings,
					'battingProbabilities' : probs['batting'],
					'pitchingProbabilities' : probs['pitching']
		}
		
		player = cls(**kwargs)
		
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
		
	def refresh(self):
		
		try:
			new = api.get_user(self.id)
			
		except TweepError:
			return False
		
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
	
	@classmethod
	def blank(cls):
	
		kwargs = {
		
					'_id' : '',
					'id' : '',
					'name' : '',
					'fullName' : '',
					'handle' : '',
					'handedness' : '',
					'uniNumber' : 0,
					'ratings' : {},
					'battingProbabilities' : {},
					'pitchingProbabilities' : {},
					'active' : True,
					'sub' : False,
					'position' : None
		}

		player = cls(**kwargs)
		
		return player
		
class Lineup(object):

	def __init__(self, battingOrder, pitchers):
	
		self.battingOrder = battingOrder
		self.pitchers = pitchers
		self.currentPitcher = pitchers.pop(0)
		self.battingOrder.append(self.currentPitcher)
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
		
	def tweetPA(self, replyTo):
		
		if self.isPitchingChange:
			tweet = "{0} enters the game to pitch, replacing {1}.".format(self.playerIn.handle, self.playerOut.handle)
		
		else:
			tweet = "{0} enters the game to pinch hit for {1}.".format(self.playerIn.handle, self.playerOut.handle)
		
		tweetID = api.update_status(tweet, in_reply_to_status_id = replyTo).id
		
		return tweetID
		
	def __str__(self):
		
		if self.isPitchingChange:
			subString = "{0} enters the game to pitch, replacing {1}.".format(self.playerIn.handle, self.playerOut.handle)
			
		else:
			subString = "{0} enters the game to pinch hit for {1}.".format(self.playerIn.handle, self.playerOut.handle)
		
		return subString
