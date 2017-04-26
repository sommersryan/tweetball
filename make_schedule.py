"""
This script loads teams from MongoDB and schedules a full tweetball season
with them
"""

import random
from pymongo import MongoClient
from config import MONGO_URI
from collections import deque

client = MongoClient(MONGO_URI)
teamColl = client.tweetball.teams

teams = list(teamColl.find())

leagues = [list(teamColl.find({'league' : 'North'})), list(teamColl.find({'league' : 'South'}))]

divisions = [list(teamColl.find({'league' : 'South', 'division' : 'East'})), list(teamColl.find({'league' : 'South', 'division' : 'West'})), 
	list(teamColl.find({'league' : 'North', 'division' : 'East'})), list(teamColl.find({'league' : 'North', 'division' : 'West'}))]

class RoundRobin(object):

	# RoundRobin implements Round Robin style tournaments for a given set of teams, passed to init as a sequence

	def __init__(self, teams):

		self.hub = teams[-1]
		self.wheel = deque(teams[:-1])
		
		