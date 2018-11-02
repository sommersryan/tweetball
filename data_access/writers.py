
def PlayerWriter(object):

	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def savePlayer(self, player):
	
		pass
		
def PlateAppearanceWriter(object):
	
	#don't know about this one. Maybe a game writer that properly
	#embeds the plate appearances properly in the game doc? 
	
	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():	
			setattr(self, key, value)
			
	def savePlateAppearance(self, plateAppearance):
	
		pass