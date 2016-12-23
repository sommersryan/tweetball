import const

class Hitting(object):
	
	def __init__(self, **kwargs):
		
		for key, value in kwargs.items():
			setattr(self, key, value)
		
		allHits = kwargs['singles'] + kwargs['doubles'] + kwargs['triples'] + kwargs['homers']
		leagueHits = const.singles.mean + const.doubles.mean + const.triples.mean + const.homers.mean
		
		self.contact = round(((allHits/kwargs['strikeouts'])/(leagueHits/const.strikeouts.mean))*5)
		
		xbh = kwargs['doubles'] + kwargs['triples'] + kwargs['homers']
		leagueXbh = const.doubles.mean + const.triples.mean + const.homers.mean
		
		self.power = round(((xbh/kwargs['singles'])/(leagueXbh/const.singles.mean))*5)
		self.discipline = round(((kwargs['walks']/(kwargs['strikeouts']+kwargs['inPlayOuts']))/(const.walks.mean/(const.strikeouts.mean+const.inPlayOuts.mean)))*5)
		self.speed = round((kwargs['steals']/const.steals.mean)*5)
		
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
			'steals' : const.steals.generateAttribute(),
			'csRate' : const.csRate.generateAttribute()
			}
			
		inst = cls(**attrs)
				
		return inst
		
class Fielding(object):
	pass
	
class Pitching(object):
	pass
	
#all player attributes as floats stored in object attributes 
#attributes modify LEAGUE_AVG constants?