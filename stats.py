from collections import Counter
from itertools import groupby
from jinja2 import Environment, FileSystemLoader
from storage import boxScoreBucket
from datetime import datetime
import os

class RateStat(object):

	def __init__(self, rate):
	
		self.rate = rate
		
	def __str__(self):
	
		if self.rate >= 1:
		
			return "{:3.3f}".format(self.rate)
			
		else:
		
			return ".{:03.0f}".format(self.rate * 1000)

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
		
		self.awayTeam = game.awayTeam
		self.homeTeam = game.homeTeam
		
		self.awayScore = game.awayScore
		self.homeScore = game.homeScore

class BoxScore(object):

	def __init__(self, game):
		
		bList = game.homeTeam.lineup.battingOrder + game.awayTeam.lineup.battingOrder
		pList = game.homeTeam.lineup.pitchers + game.awayTeam.lineup.pitchers
		
		self.batters = {}
		self.pitchers = {}
		
		self.doubles = Counter()
		self.triples = Counter()
		self.HR = Counter()
		self.hHBP = Counter()
		self.pHBP = Counter()
		
		self.linescore = LineScore(game)
		
		for b in bList:
		
			self.batters.update({ b : Counter() })
			
		for p in pList:

			self.pitchers.update({ p : Counter() })
			
		for pa in game.PAs:
		
			self.pitchers[pa.pitcher][pa.event.type] += 1
			self.batters[pa.batter][pa.event.type] += 1
			self.batters[pa.batter]['RBI'] += pa.runs
			self.pitchers[pa.pitcher]['R'] += pa.runs
			self.batters[pa.batter]['PA'] += 1
			self.pitchers[pa.pitcher]['BF'] += 1
			
			if pa.event.type == 'double':
				self.doubles[pa.batter.name] += 1
				
			if pa.event.type == 'triple':
				self.triples[pa.batter.name] += 1
				
			if pa.event.type == 'HR':
				self.HR[pa.batter.name] += 1
				
			if pa.event.type == 'HBP':
				self.hHBP[pa.batter.name] += 1
				self.pHBP[pa.pitcher.name] += 1
			
			if pa.event.type in ['single', 'double', 'triple', 'HR']:
				self.batters[pa.batter]['H'] += 1
				self.pitchers[pa.pitcher]['H'] += 1

			if pa.event.type not in ['BB', 'HBP', 'sacrifice']:
				self.batters[pa.batter]['AB'] += 1

		for k in list(self.batters.keys()):
			
			self.batters[k]['AVG'] = RateStat(self.batters[k]['H'] / self.batters[k]['AB'])
			outs = self.batters[k]['inPlayOut'] + self.batters[k]['strikeout']
			self.batters[k]['OBP'] = RateStat((self.batters[k]['PA'] - outs) / self.batters[k]['PA'])
			tb = self.batters[k]['single']
			tb += self.batters[k]['double'] * 2
			tb += self.batters[k]['triple'] * 3
			tb += self.batters[k]['HR'] * 4
			self.batters[k]['SLG'] = RateStat(tb / self.batters[k]['AB'])
		
		for k in list(self.pitchers.keys()):
		
			pitcherPAs = [a for a in game.PAs if a.pitcher == k]
			
			if len(pitcherPAs) > 0:
				ip = (pitcherPAs[-1].inning - pitcherPAs[0].inning)
			
				if pitcherPAs[-1].endState.outs == 3:
					ip += 1
				
				elif pitcherPAs[-1].endState.outs == 2:
					ip += 0.6666
				
				elif pitcherPAs[-1].endState.outs == 1:
					ip += 0.3333
				
				self.pitchers[k]['IP'] = ip
				self.pitchers[k]['RA'] = (self.pitchers[k]['R'] / self.pitchers[k]['IP']) * 9

	def html(self):
		
		env = Environment(loader = FileSystemLoader(os.getcwd()), trim_blocks = True)
		
		cols = len(self.linescore.tops)
		header = [i for i in range(1, cols+1)]
		
		kwargs = {
					'header' : header,
					'tops' : self.linescore.tops,
					'bottoms' : self.linescore.bottoms,
					'awayTeam' : self.linescore.awayTeam,
					'homeTeam' : self.linescore.homeTeam,
					'batters' : self.batters,
					'pitchers' : self.pitchers,
					'doubles' : self.doubles,
					'triples' : self.triples,
					'homers' : self.HR,
					'hHBP' : self.hHBP,
					'pHBP' : self.pHBP
				}
		
		return env.get_template('box.html').render(**kwargs)
	
	def save(self):
		
		n = '{:%Y%m%d}.html'.format(datetime.utcnow())
		k = boxScoreBucket.new_key(n)
		k.set_contents_from_string(self.html().encode('utf-8'))
		k.set_canned_acl('public-read')
		
		url = k.generate_url(expires_in=0, query_auth=False)
		
		return url
	
class PlayerStats(object):

	pass