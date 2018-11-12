import pymongo
import json
import os
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, CURRENT_SEASON
from fractions import Fraction
from collections import Counter
from game_engine.play import Event
from bson.objectid import ObjectId

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

playerList = list(db.players.find())
legacyGameId = os.environ.get('LEGACY_GAME_ID')
legacyPlayerId = os.environ.get('LEGACY_PLAYER_ID')

eventTypes = ['strikeout', 'sacrifice', 'GDP', 'inPlayOut',
	'single', 'double', 'triple', 'HR', 'HBP', 'BB', 'error']

for count, player in enumerate(playerList):
	
	print("Processing {0} of {1} : {2}".format(count, len(playerList), player['name']))
	
	oldProbs = player.pop('probabilities')
	
	player['pitchingProbabilities'] = oldProbs['pitching']
	player['battingProbabilities'] = oldProbs['batting']
	
	for e in eventTypes:
		
		try:
			for i in range(0, player['stats']['0']['pitching'][e]):
			
				newEvent = {
					'game_id' : ObjectId(legacyGameId),
					'game_ordinal' : 0,
					'top' : False,
					'inning' : 1,
					'awayScore' : 0,
					'homeScore' : 0,
					'batterId' : ObjectId(legacyPlayerId),
					'pitcherId' : player['_id'],
					'narratives' : [],
					'isSubstitution' : False,
					'wpa' : 0,
					'baseState' : {},
					'endState' : {},
					'runs' : 0,
					'timestamp' : datetime.utcnow(),
					'event' : Event(e).__dict__
				}
				
				db.events.insert_one(newEvent)
				
		except KeyError:
			continue
				
	for e in eventTypes:
	
		try:
			for i in range(0, player['stats']['0']['batting'][e]):
			
				newEvent = {
					'game_id' : ObjectId(legacyGameId),
					'game_ordinal' : 0,
					'top' : False,
					'inning' : 1,
					'awayScore' : 0,
					'homeScore' : 0,
					'batterId' : player['_id'],
					'pitcherId' : ObjectId(legacyPlayerId),
					'narratives' : [],
					'isSubstitution' : False,
					'wpa' : 0,
					'baseState' : {},
					'endState' : {},
					'runs' : 0,
					'timestamp' : datetime.utcnow(),
					'event' : Event(e).__dict__
				}
				
				db.events.insert_one(newEvent)
				
		except KeyError:
			continue
			
	player.pop('stats')
	
	db.players.find_one_and_replace({'_id' : player['_id']}, player)