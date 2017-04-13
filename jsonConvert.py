from storage import playerStore
from roster import Player
from pymongo import MongoClient
import json

# The purpose of this script is to load player objects from AWS and convert them for
# storage into a mongodb database, to facilitate upgrading tweetball to a fixed-roster,
# extensible app, and the addition of a website for viewing statistics

# initialize client and database

client = MongoClient()

db = client.tweetball

# initialize player collection

playerColl = db.players
	
# Load all player keys from AWS

allPlayers = list(playerStore.list())

total = len(allPlayers)
count = 0

# Iterate through player keys

for key in allPlayers:

	# load player's object
	
	player = Player.load(key)
	
	# the Fraction object in pitcher IP is not serializable; requires special handling
	
	ipNum = player.pitchingCareerStats['IP'].numerator
	ipDenom = player.pitchingCareerStats['IP'].denominator
	
	try:
		player.pitchingCareerStats.pop('IP')
	
	except KeyError:
		pass
	
	# just in case:
	
	player.pitchingGameStats.clear()
	player.battingGameStats.clear()
	
	# dump to JSON string
	
	playerJSONString = json.dumps(player, default= lambda o : o.__dict__)
	
	# serialize to JSON object (dict really) for editing
	
	playerDict = json.loads(playerJSONString)
	
	# remove some keys we won't need
	
	[playerDict.pop(k) for k in ['active', 'sub', 'position', 'battingGameStats', 'pitchingGameStats']]
	
	# move probabilities out of ratings so it makes sense
	
	playerDict['probabilities'] = {}
	
	playerDict['probabilities']['batting'] = playerDict['ratings'].pop('batting')
	playerDict['probabilities']['pitching'] = playerDict['ratings'].pop('pitching')
	
	# rearrange stats for extensibility
	
	playerDict['stats'] = {}
	playerDict['stats']['seasons'] = {}
	playerDict['stats']['seasons']["0"] = {}
	
	playerDict['stats']['seasons']["0"]['batting'] = playerDict.pop('battingCareerStats')
	playerDict['stats']['seasons']["0"]['pitching'] = playerDict.pop('pitchingCareerStats')
	
	# add back in IP
	
	playerDict['stats']['seasons']["0"]['pitching']['IP'] = {}
	playerDict['stats']['seasons']["0"]['pitching']['IP']['numerator'] = ipNum
	playerDict['stats']['seasons']["0"]['pitching']['IP']['denominator'] = ipDenom
	
	# adding a field for twitter avatar URL (will implement later)
	
	playerDict['avatarURL'] = ""
	
	playerColl.insert_one(playerDict)
	
	count += 1
	
	print ("Player {0} ({1} of {2}) added".format(player.handle, count, total))
	
	# dump to JSON file (dump them all to one file? maybe)
	
	#with open("{0}.json".format(player.id), 'w') as output:
	#	json.dump(playerDict, output)
	
	
	
	