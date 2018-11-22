from .schema import *
from .api_access import API

api = API()
pa_schema = PlateAppearanceSchema()

class PlayerWriter(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def save_player(self, player):
	
		pass
		
class PlateAppearanceWriter(object):
	
	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def save_plate_appearance(self, plateAppearance):
	
		paJson = pa_schema.dumps(plateAppearance).data
		
		result = api.post_event(paJson)
		
		return result
		
class GameWriter(object):

	def __init__(self, **kwargs):
	
		for key, value in kwargs.items():	
			setattr(self, key, value)
		
	def save_game(self, game):
	
		gs = GameSchema()
		
		game_json = gs.dumps(game).data
		
		resp = api.post_game(game_json)
		
		return resp