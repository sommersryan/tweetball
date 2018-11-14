from .schema import *
from .api_access import API

api = API()
pa_schema = PlateAppearanceSchema()

def PlayerWriter(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def savePlayer(self, player):
	
		pass
		
def PlateAppearanceWriter(object):
	
	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def savePlateAppearance(self, plateAppearance):
	
		paJson = pa_schema.dumps(plateAppearance)
		
		result = api.post_event(paJson)
		
		return result.json()
		
		
		
		