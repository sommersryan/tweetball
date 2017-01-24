from config import CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, ACCESS_SECRET, NUM_PAS, PA_TIME
import tweepy, time

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)

class GameTweeter(object):

	def __init__(self, game):
	
		self.game = game
		
		sortWPA = sorted(game.PAs, key = lambda x: abs(x.wpa))
		
		self.threshold = abs(sortWPA[-NUM_PAS].wpa)
		
	def execute(self):
	
		for pa in self.game.PAs:
		
			if abs(pa.wpa) >= self.threshold:
			
				pa.tweetPA()
			
			time.sleep(PA_TIME)
		
		return True