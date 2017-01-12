from collections import Counter
from itertools import groupby
from jinja2 import Environment, FileSystemLoader
import os

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
		
		if len(self.bottoms) < len(self.tops):
			self.bottoms += ['x']
		
		self.awayTeam = game.awayTeam.location
		self.homeTeam = game.homeTeam.location
		
		self.awayScore = game.awayScore
		self.homeScore = game.homeScore

	def html(self):
		
		env = Environment(loader = FileSystemLoader(os.getcwd()), trim_blocks = True)
		
		cols = len(self.tops)
		header = [i for i in range(1, cols+1)]
		
		return env.get_template('box.html').render(header = header, tops = self.tops, 
									bottoms = self.bottoms, awayTeam = self.awayTeam, 
									homeTeam = self.homeTeam)
	
class BoxScore(object):

	def __init__(self, game):
		
		bList = game.homeTeam.lineup.battingOrder + game.awayTeam.lineup.battingOrder
		self.batters = {}

		for b in bList:
		
			self.batters.update({ b : Counter() })
			
		for pa in game.PAs:
		
			self.batters[pa.batter][pa.event.type] += 1
			self.batters[pa.batter]['RBI'] += pa.runs
			self.batters[pa.batter]['PA'] += 1
			
			if pa.event.type in ['single', 'double', 'triple', 'HR']:
				self.batters[pa.batter]['H'] += 1
			
			if pa.event.type not in ['BB', 'HBP', 'sacrifice']:
				self.batters[pa.batter]['AB'] += 1
		
		for k in list(self.batters.keys()):
			
			self.batters[k]['AVG'] = self.batters[k]['H'] / self.batters[k]['AB']
			outs = self.batters[k]['inPlayOut'] + self.batters[k]['strikeout']
			self.batters[k]['OBP'] = (self.batters[k]['PA'] - outs) / self.batters[k]['PA']
			tb = self.batters[k]['single']
			tb += self.batters[k]['double'] * 2
			tb += self.batters[k]['triple'] * 3
			tb += self.batters[k]['HR'] * 4
			self.batters[k]['SLG'] = tb / self.batters[k]['AB']
			
class PlayerStats(object):

	pass