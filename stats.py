from collections import Counter
from itertools import groupby
from jinja2 import Environment, FileSystemLoader

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
		
		env = Environment(loader = FileSystemLoader('/'), trim_blocks = True)
		
		cols = len(self.bottoms)
		header = [i for i in range(1, cols+1)]
		
		return env.get_template('box.html').render(header = header, tops = self.tops, bottoms = self.bottoms, awayTeam = self.awayTeam, homeTeam = self.homeTeam)
		
class BoxScore(object):

	pass