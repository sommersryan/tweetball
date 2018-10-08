import csv
from pymongo import MongoClient
from config import MONGO_URI

# Importing teams from a csv file formatted like the one in this repo

#Connect to mongo

client = MongoClient(MONGO_URI)
teamsColl = client.tweetball.teams

# Open the CSV file, use DictReader to convert entries to 
# dicts with appropriate field names

f = open('teams.csv','r')
fields = ['city', 'nickname', 'league', 'division', 'lat', 'long']
reader = csv.DictReader(f,fields)

# Modify the dicts so that lat and long are part of an embedded "coordinates" doc
# Finally, insert into db

teams = list(reader)

for t in teams:

	t['coordinates'] = {}
	t['coordinates']['lat'] = t.pop('lat')
	t['coordinates']['long'] = t.pop('long')
	
	teamsColl.insert(t)

