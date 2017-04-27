"""
This script loads teams from MongoDB and schedules a full tweetball season
with them
"""

import random
from pymongo import MongoClient
from config import MONGO_URI
from collections import deque

class RoundRobin(object):

	# RoundRobin implements Round Robin style tournaments for a given set of teams, passed to init as a sequence

	def __init__(self, teams):

		self.teams = teams
		# If the list of teams are uneven, append a bye match
		
		if len(teams) % 2 == 1:
			self.teams.append('BYE')
		
		self.mid = int(len(self.teams)/2)
		self.matches = []
		
	def makeRound(self):
	
		# Adds one round of matches, as tuples, to the match list
		# Switch is a boolean, if true the home/away ordering is flipped
	
		left = self.teams[:self.mid]
		right = list(reversed(self.teams[self.mid:]))
		round = []
		
		for i in range(0, self.mid):
			
			round.append((left[i], right[i]))
		
		self.matches.append(round)
		
		return True	
			
	def rotate(self):
	
		# Rotate the "wheel" clockwise, keeping the hub (index 0) in place
		
		wheel = deque(self.teams[1:])
		wheel.rotate(1)
		self.teams = [self.teams[0]] + list(wheel)
		
		return True
		
	def makeAllRounds(self):
	
		# Appends a complete set of round robin matches
		# Alternate is boolean, if True, round alternates flipping home/away teams
		
		for i in range(0, len(self.teams)-1):
			
			self.makeRound()
			self.rotate()
			
		return True
		
def main():
	
	client = MongoClient(MONGO_URI)
	teamColl = client.tweetball.teams

	teams = list(teamColl.find())

	leagues = [list(teamColl.find({'league' : 'North'})), list(teamColl.find({'league' : 'South'}))]

	divisions = [list(teamColl.find({'league' : 'South', 'division' : 'East'})), list(teamColl.find({'league' : 'South', 'division' : 'West'})), 
		list(teamColl.find({'league' : 'North', 'division' : 'East'})), list(teamColl.find({'league' : 'North', 'division' : 'West'}))]
		
if __name__ == '__main__':
	main()