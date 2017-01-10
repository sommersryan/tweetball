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
		
		cols = max(len(self.tops), len(self.bottoms))
		header = "<th>TEAM</th>"
		
		for i in range(1, cols+1):
			header += "<th>{0}</th>".format(i)
		
		awayLine = "<td>{0}</td>".format(self.awayTeam)
		
		for i in self.tops:
			awayLine += "<td>{0}</td>".format(i)
			
		homeLine = "<td>{0}</td>".format(self.homeTeam)
		
		for i in self.bottoms:
			homeLine += "<td>{0}</td>".format(i)
			
		return "<table><tr>{0}</tr><tr>{1}</tr><tr>{2}</tr></table>".format(header, awayLine, homeLine)
		
class BoxScore(object):

	pass