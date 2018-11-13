from .schema import *
from .api_access import API
import json

api = API()

player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)

class PlayerFactory(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def load_players(self, players_json):
	
		players = json.loads(players_json)['_items']
	
		return players_schema.load(players).data
			
	def load_player_by_id(self, objectId):
	
		player_json = api.get_player_by_id(objectId)
		
		return player_schema.loads(player_json).data
	
	def load_player_by_handle(self, handle):
	
		player_json = api.get_player_by_handle(handle)
		
		return player_schema.loads(player_json).data
	
def load_player_pool():
		
	fac = PlayerFactory()
	
	playersJSON = api.get_players(sort_key='lastStart', count=24)
	
	pool = fac.load_players(playersJSON)
	
	for p in pool:
		p.refresh()
		
	pool.sort(key = lambda x: (x.ratings['control'] + x.ratings['stuff']), reverse = False)
	homeHitters, homePitchers, awayHitters, awayPitchers = [], [], [], []
	
	for i in range(0,8):
		homeHitters.append(pool.pop())
		awayHitters.append(pool.pop())
		
	for i in range(0,4):
		homePitchers.append(pool.pop())
		awayPitchers.append(pool.pop())
		
	return { 'awayHitters' : awayHitters, 'awayPitchers' : awayPitchers, 
		'homeHitters' : homeHitters, 'homePitchers' : homePitchers }