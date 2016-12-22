import const

class Hitting(object):
	
	def __init__(self, singles = const.singles.mean, doubles = const.doubles.mean,
			triples = const.triples.mean, homers = const.homers.mean, strikeouts = const.strikeouts.mean, 
			walks = const.walks.mean, hbp = const.hbp.mean, inPlayOuts = const.inPlayOuts.mean,
			steals = const.steals.mean, csRate = const.csRate.mean):
		
		#Initializes an attribute set of an average hitter
		
		self.singles = singles
		self.doubles = doubles
		self.triples = triples
		self.homers = homers
		self.strikeouts = strikeouts
		self.walks = walks
		self.hbp = hbp
		self.inPlayOuts = inPlayOuts
		self.steals = steals
		self.csRate = csRate
		
		allHits = singles + doubles + triples + homers
		leagueHits = const.singles.mean + const.doubles.mean + const.triples.mean + const.homers.mean
		
		self.contact = round(((allHits/strikeouts)/(leagueHits/const.strikeouts.mean))*5)
		
		xbh = doubles + triples + homers
		leagueXbh = const.doubles.mean + const.triples.mean + const.homers.mean
		
		self.power = round(((xbh/singles)/(leagueXbh/const.singles.mean))*5)
		self.discipline = round(((walks/(strikeouts+inPlayOuts))/(const.walks.mean/(const.strikeouts.mean+const.inPlayOuts.mean)))*5)
		self.speedRating = round((steals/const.steals.mean)*5)
		
	@classmethod
	def random(cls):
	
		#Creates a random hitting skillset
		
		singles = const.singles.generateAttribute()
		doubles = const.doubles.generateAttribute()
		triples = const.triples.generateAttribute()
		homers = const.homers.generateAttribute()
		strikeouts = const.strikeouts.generateAttribute()
		walks = const.walks.generateAttribute()
		hbp = const.hbp.generateAttribute()
		inPlayOuts = const.inPlayOuts.generateAttribute()
		steals = const.steals.generateAttribute()
		csRate = const.csRate.generateAttribute()
		
		inst = cls(singles, doubles, triples, homers, strikeouts, walks,
				hbp, inPlayOuts, steals, csRate)
				
		return inst
		
class Fielding(object):
	pass
	
class Pitching(object):
	pass
	
#all player attributes as floats stored in object attributes 
#attributes modify LEAGUE_AVG constants?