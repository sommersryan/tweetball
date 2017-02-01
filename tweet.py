from config import CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, ACCESS_SECRET, NUM_PAS, PA_TIME
import tweepy, time

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)

class GameTweeter(object):

	def __init__(self, game):
	
		self.game = game
		
		self.intro = "{0} at {1}".format(game.awayTeam, game.homeTeam)
		
		self.awayLineupTop = "{0} (a)\r\n".format(game.awayTeam)
		self.homeLineupTop = "{0} (h)\r\n".format(game.homeTeam)
		self.awayLineupBot = "{0} (a) cont.\r\n".format(game.awayTeam)
		self.homeLineupBot = "{0} (h) cont.\r\n".format(game.homeTeam)
		
		for i, p in enumerate(game.awayTeam.lineup.battingOrder[:5]):
		
			self.awayLineupTop += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
			
		for i, p in enumerate(game.homeTeam.lineup.battingOrder[:5]):
		
			self.homeLineupTop += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
		
		for i, p in enumerate(game.awayTeam.lineup.battingOrder[5:]):
		
			self.awayLineupBot += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
			
		for i, p in enumerate(game.homeTeam.lineup.battingOrder[5:]):
		
			self.homeLineupBot += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
		
		sortWPA = sorted(game.PAs, key = lambda x: abs(x.wpa))
		
		self.threshold = abs(sortWPA[-NUM_PAS].wpa)
		
	def execute(self):
	
		for i, pa in enumerate(self.game.PAs):
		
			if abs(pa.wpa) >= self.threshold or i == len(self.game.PAs)-1:
			
				pa.tweetPA()
			
			time.sleep(PA_TIME)
		
		return True