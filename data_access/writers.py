
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
	
		pass