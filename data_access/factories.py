from .schema import *
from .api_access import API

api = API()

player_schema = PlayerSchema()

class PlayerFactory(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def get_player_by_id(self, objectId):
	
		player_json = api.get_player_by_id(objectId)
		
		return player_schema.loads(player_json).data
	
	def get_player_by_handle(self, handle):
	
		player_json = api.get_player_by_handle(handle)
		
		return player_schema.loads(player_json).data
	
class TeamFactory(object):

	def __init__(self, **kwargs):
	
		for key, value in kwargs.items():
			setattr(self, key, value)
			
	def get_Teams(self):
	
		pass