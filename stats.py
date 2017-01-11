from collections import Counter
from itertools import groupby

class LineScore(object):

	def __init__(self, game):
	
		self.innings = []
		
		for key, group in groupby(game.PAs, key = lambda x : x.top):
			self.innings.append(list(group))
			
		self.scores = []
		
		for i in self.innings:
			self.scores.append(sum([pa.runs for pa in i]))
			
		self.tops = self.scores[::2]
		self.bottoms = self.scores[1::2]
		
		self.awayTeam = game.awayTeam.location
		self.homeTeam = game.homeTeam.location
		
		self.awayScore = game.awayScore
		self.homeScore = game.homeScore

	def html(self):
		
		cols = len(self.bottoms)
		
		header = [i for i in range(1, cols+1)]
		
		return render_template('box.html', header=header, tops=self.tops, bottoms=self.bottoms)
		
class BoxScore(object):

	pass