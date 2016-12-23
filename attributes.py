import const, config
from utils import log5, weightedChoice

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

		oc = { key : atts[key] for key in config.RESULT_TYPES }
		
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

class Matchup(object):

	def __init__(self, hitter, pitcher):
	
		for key in config.RESULT_TYPES:
		
			resultProb = log5(pitcher[key], hitter[key], const.LG_OUTCOMES[key])
			
			setattr(self, key, resultProb)
			
	def genResult(self):
	
		return weightedChoice(self.__dict__)
		