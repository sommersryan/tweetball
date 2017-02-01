from config import CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, ACCESS_SECRET, NUM_PAS, PA_TIME
import tweepy, time, stats

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
			if not p.sub:
				self.awayLineupTop += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
			
		for i, p in enumerate(game.homeTeam.lineup.battingOrder[:5]):
			if not p.sub:
				self.homeLineupTop += "{0}. {1} {2}\r\n".format(i+1, p.handle, p.position)
		
		for i, p in enumerate(game.awayTeam.lineup.battingOrder[5:]):
			if not p.sub:
				self.awayLineupBot += "{0}. {1} {2}\r\n".format(i+6, p.handle, p.position)
			
		for i, p in enumerate(game.homeTeam.lineup.battingOrder[5:]):
			if not p.sub:
				self.homeLineupBot += "{0}. {1} {2}\r\n".format(i+6, p.handle, p.position)
		
		bs = stats.BoxScore(self.game)
		self.boxURL = bs.save()
		
		self.closeOut = "{0} {1}, {2} {3}\r\n {4}".format(self.game.awayTeam, self.game.awayScore, self.game.homeTeam, self.game.homeScore, self.boxURL)
		
		sortWPA = sorted(game.PAs, key = lambda x: abs(x.wpa))
		
		self.threshold = abs(sortWPA[-NUM_PAS].wpa)
		
	def execute(self):
		
		prevID = api.update_status(self.intro).id
		
		time.sleep(60)
		
		prevID = api.update_status(self.awayLineupTop, in_reply_to_status_id = prevID).id
		
		time.sleep(5)
		
		prevID = api.update_status(self.awayLineupBot, in_reply_to_status_id = prevID).id
		
		time.sleep(30)
		
		prevID = api.update_status(self.homeLineupTop, in_reply_to_status_id = prevID).id
		
		time.sleep(5)
		
		prevID = api.update_status(self.homeLineupBot, in_reply_to_status_id = prevID).id
		
		time.sleep(60)
		
		for i, pa in enumerate(self.game.PAs):
		
			if abs(pa.wpa) >= self.threshold or i == len(self.game.PAs)-1:
			
				prevID = pa.tweetPA(prevID)
			
			time.sleep(PA_TIME)
		
		time.sleep(60)
		
		api.update_status(self.closeOut, in_reply_to_status_id = prevID)
		
		return True