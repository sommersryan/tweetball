import const

class Attributes(object):
	
	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():
			setattr(self, key, value)
		
	@classmethod
	def random(cls):
	
		#Creates a random hitting skillset
		attrs = {
			'singles' : const.singles.generateAttribute(),
			'doubles' : const.doubles.generateAttribute(),
			'triples' : const.triples.generateAttribute(),
			'homers' : const.homers.generateAttribute(),
			'strikeouts' : const.strikeouts.generateAttribute(),
			'walks' : const.walks.generateAttribute(),
			'hbp' : const.hbp.generateAttribute(),
			'inPlayOuts' : const.inPlayOuts.generateAttribute(),
			}
			
		inst = cls(**attrs)
				
		return inst
	
	def outcomes(self):
	
		atts = self.__dict__
		
		keys = ['singles','doubles','triples','homers',
			'strikeouts','walks','hbp','inPlayOuts']
		
		oc = { key : atts[key] for key in keys }
		
		return oc

class Hitting(Attributes):
	
	def __init__(self, **kwargs):
	
		super().__init__(**kwargs)

	@classmethod
	def random(cls):
		
		inst = super().random()
		
		inst.steals = const.steals.generateAttribute()
		inst.csRate = const.csRate.generateAttribute()
		
		return inst
		
class Pitching(Attributes):

	def __init__(self, **kwargs):
	
		super().__init__(**kwargs)

	