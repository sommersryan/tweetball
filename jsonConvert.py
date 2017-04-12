from storage import playerStore
from roster import Player
import json

# Load all player keys from AWS

allPlayers = list(playerStore.list())

# Iterate through player keys

for key in allPlayers:

	# load player's object
	
	player = Player.load(key)
	
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
	palyerDict['stats']['seasons'][0] = {}
	
	playerDict['stats']['seasons'][0]['batting'] = playerDict.pop('battingCareerStats')
	playerDict['stats']['seasons'][0]['pitching'] = playerDict.pop('pitchingCareerStats')
	
	# dump to JSON file (dump them all to one file? maybe)
	
	with open("{0}.json".format(player.id), 'w') as output:
		json.dump(playerDict, output)
	
	
	
	