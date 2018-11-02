
class PlayerFactory(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def getPlayer(self, objectId):
	
		pass		
	
	
class TeamFactory(object):

	def __init__(self, **kwargs):
	
		for key, value in kwargs.items():
			setattr(self, key, value)
			
	def getTeams(self):
	
		pass