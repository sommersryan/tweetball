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

# take a league, make a deque of each division
# use the for -> for -> append and rotate method to make a list of series
# sort series by away and then home (list.sort(key = lambda x: (x[0], x[1])))
# starting at index 0, 2, 4, 6, flip series (x.reverse) and every series at index + 9*1, 9*2, 9*3, 9*4 etc 
# should get even home away number series for each team


