import json, bson, datetime
from mongo_player_store import serializePlayerAttribute
from roster import Team, Player, Lineup
from pymongo import MongoClient
from config import MONGO_URI, CURRENT_SEASON

client = MongoClient(MONGO_URI)
db = client.tweetball

def serializePlateAppearance(plateAppearance):
	
	del plateAppearance.matchup
	del plateAppearance.transitions
	
	paString = json.dumps(plateAppearance, default = lambda att : serializePlateAppearanceAttribute(att))
	paDict = json.loads(paString)
	
	return paDict
	
def serializePlateAppearanceAttribute(attribute):
	
	if isinstance(attribute, Player):
		pString = json.dumps(attribute, default = lambda att: serializePlayerAttribute(att))
		pDict = json.loads(pString)
		[pDict.pop(a) for a in ['battingCareerStats', 'battingGameStats', 'pitchingCareerStats', 'pitchingGameStats', 'ratings']]
		return pDict
		
	else:
		return attribute.__dict__
		
def serializeLineupAttribute(lineupAttribute):

	if isinstance(lineupAttribute, Player):
		pString = json.dumps(lineupAttribute, default = lambda att: serializePlayerAttribute(att))
		pDict = json.loads(pString)
		[pDict.pop(a) for a in ['battingCareerStats', 'battingGameStats', 'pitchingCareerStats', 'pitchingGameStats', 'ratings']]
		return pDict
		
	else:
		return lineupAttribute.__dict__
		
def serializeTeamAttribute(teamAttribute):

	if isinstance(teamAttribute, Lineup):
		return json.loads(json.dumps(teamAttribute, default = lambda att: serializeLineupAttribute(att)))
		
	else:
		return teamAttribute.__dict__
		
def serializeGame(game):
	
	gameDict = {}
	
	gameDict['plateAppearances'] = [serializePlateAppearance(a) for a in game.PAs]
	gameDict['homeTeam'] = json.loads(json.dumps(game.homeTeam, default = lambda att: serializeTeamAttribute(att)))
	gameDict['awayTeam'] = json.loads(json.dumps(game.awayTeam, default = lambda att: serializeTeamAttribute(att)))
	
	for attr in ['homeScore', 'awayScore', 'complete']:
		gameDict[attr] = getattr(game, attr)
		
	gameDict['startTime'] = game.startTime
	
	return gameDict

def mongoGameSave(game):

	mongoGame = serializeGame(game)
	
	db.games.insert_one(mongoGame)

	
	