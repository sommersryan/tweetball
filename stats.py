	from collections import Counter
from itertools import groupby
from jinja2 import Environment, FileSystemLoader
from storage import boxScoreBucket
from datetime import datetime
from functools import total_ordering
import os

@total_ordering
class RateStat(object):

	def __init__(self, rate):
	
		self.rate = rate
	
	def __add__(self, num):
	
		return RateStat(0)
	
	def __radd__(self, num):
	
		return RateStat(0)
		
	def __eq__(self, num):
	
		return self.rate == num
		
	def __lt__(self, num):
	
		return self.rate < num
	
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
		
		self.game = game
		self.linescore = LineScore(game)
		
		for batter in game.awayTeam.lineup.battingOrder:
		
			if batter.battingGameStats['AB'] > 0:
				batter.battingGameStats['AVG'] = RateStat(batter.battingGameStats['H'] / batter.battingGameStats['AB'])
				tb = batter.battingGameStats['single']
				tb += (batter.battingGameStats['double'] * 2)
				tb += (batter.battingGameStats['triple'] * 3)
				tb += (batter.battingGameStats['HR'] * 4)
			
				batter.battingGameStats['SLG'] = RateStat(tb / batter.battingGameStats['AB'])
			
			else:
				batter.battingGameStats['AVG'] = RateStat(0)
				batter.battingGameStats['SLG'] = RateStat(0)
				
			if batter.battingGameStats['PA'] > 0:
				batter.battingGameStats['OBP'] = RateStat(1 - ((batter.battingGameStats['strikeout'] + batter.battingGameStats['inPlayOut']) / batter.battingGameStats['PA']))
			
			else:
				batter.battingGameStats['OBP'] = RateStat(0)
			
		for batter in game.homeTeam.lineup.battingOrder:
			
			if batter.battingGameStats['AB'] > 0:
				batter.battingGameStats['AVG'] = RateStat(batter.battingGameStats['H'] / batter.battingGameStats['AB'])			
				tb = batter.battingGameStats['single']
				tb += (batter.battingGameStats['double'] * 2)
				tb += (batter.battingGameStats['triple'] * 3)
				tb += (batter.battingGameStats['HR'] * 4)
			
				batter.battingGameStats['SLG'] = RateStat(tb / batter.battingGameStats['AB'])
		
			else:
				batter.battingGameStats['AVG'] = RateStat(0)
				batter.battingGameStats['SLG'] = RateStat(0)
				
			if batter.battingGameStats['PA'] > 0:
				batter.battingGameStats['OBP'] = RateStat(1 - ((batter.battingGameStats['strikeout'] + batter.battingGameStats['inPlayOut']) / batter.battingGameStats['PA']))
			
			else:
				batter.battingGameStats['OBP'] = RateStat(0)

		for pitcher in game.awayTeam.lineup.usedPitchers:
		
			if pitcher.pitchingGameStats['BF'] > 0:
			
				if pitcher.pitchingGameStats['IP'] == 0:
					pitcher.pitchingGameStats['RA'] = float("inf")
					
				else:
					pitcher.pitchingGameStats['RA'] = (pitcher.pitchingGameStats['R'] / float(pitcher.pitchingGameStats['IP'])) * 9
					
			ip = pitcher.pitchingGameStats['IP'].__floor__()
			r = pitcher.pitchingGameStats['IP'] - ip
			
			if r.numerator == 1:
				ip += .1
				
			if r.numerator == 2:
				ip += .2
					
			pitcher.pitchingGameStats['printIP'] = ip
			
		for pitcher in game.homeTeam.lineup.usedPitchers:
		
			if pitcher.pitchingGameStats['BF'] > 0:
				
				if pitcher.pitchingGameStats['IP'] == 0:
					pitcher.pitchingGameStats['RA'] = float("inf")
					
				else:
					pitcher.pitchingGameStats['RA'] = (pitcher.pitchingGameStats['R'] / float(pitcher.pitchingGameStats['IP'])) * 9
				
			
			ip = pitcher.pitchingGameStats['IP'].__floor__()
			r = pitcher.pitchingGameStats['IP'] - ip
			
			if r.numerator == 1:
				ip += .1
				
			if r.numerator == 2:
				ip += .2
					
			pitcher.pitchingGameStats['printIP'] = ip
			
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
					'game' : self.game
				}
		
		return env.get_template('box.html').render(**kwargs)
	
	def save(self, name='{:%Y%m%d%H%M}'.format(datetime.utcnow())):
		
		n = name
		k = boxScoreBucket.new_key(n)
		k.set_metadata('Content-Type', 'text/html')
		k.set_contents_from_string(self.html().encode('utf-8'))
		k.set_canned_acl('public-read')
		
		url = k.generate_url(expires_in=0, query_auth=False)
		
		return url