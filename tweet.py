from config import CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, ACCESS_SECRET, NUM_PAS, PA_TIME
import tweepy, time, stats

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)

class GameTweeter(object):

	def __init__(self, game):
	
		self.game = game
		
		self.intro = "{0} at {1}".format(game.awayTeam, game.homeTeam)
		
		self.awayLineup = "{0} (a)\r\n".format(game.awayTeam)
		self.homeLineup = "{0} (h)\r\n".format(game.homeTeam)
		
		num = 1
		
		for p in game.awayTeam.lineup.battingOrder:
			if not p.sub:
				self.awayLineup += "{0}. {1} {2}\r\n".format(num, p.handle, p.position)
				num += 1
				
		num = 1
		
		for p in game.homeTeam.lineup.battingOrder:
			if not p.sub:
				self.homeLineup += "{0}. {1} {2}\r\n".format(num, p.handle, p.position)
				num += 1
				
		bs = stats.BoxScore(self.game)
		self.boxURL = bs.save()
		
		self.closeOut = "{0} {1}, {2} {3}\r\n {4}".format(self.game.awayTeam, self.game.awayScore, self.game.homeTeam, self.game.homeScore, self.boxURL)
		
		sortWPA = sorted(game.PAs, key = lambda x: abs(x.wpa))
		
		self.threshold = abs(sortWPA[-NUM_PAS].wpa)
		
	def execute(self):
		
		prevID = api.update_status(self.intro).id
		
		time.sleep(60)
		
		prevID = api.update_status(self.awayLineup, in_reply_to_status_id = prevID).id
		
		time.sleep(30)
		
		prevID = api.update_status(self.homeLineup, in_reply_to_status_id = prevID).id
		
		time.sleep(60)
		
		for i, pa in enumerate(self.game.PAs):
		
			if abs(pa.wpa) >= self.threshold or pa.runs > 0 or i == len(self.game.PAs)-1:
			
				prevID = pa.tweetPA(prevID)
			
			time.sleep(PA_TIME)
		
		time.sleep(60)
		
		api.update_status(self.closeOut, in_reply_to_status_id = prevID)
		
		return True