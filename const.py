import random

class Constant(object):
	def __init__(self, mean, stdDev):
		self.mean = mean
		self.stdDev = stdDev
	
	def generateAttribute(self):
		att = random.normalvariate(self.mean, self.stdDev)
		
		if att > 1:
			att = 1
			
		if att < 0:
			att = 0
			
		return att
		
singles = Constant(0.149197,0.032242)
doubles = Constant(0.044724,0.013545)
triples = Constant(0.004730,0.005326)
homers = Constant(0.030394,0.015656)
strikeouts = Constant(0.211199,0.061989)
walks = Constant(0.081744,0.03009)
hbp = Constant(0.008945,0.008299)
inPlayOuts = Constant(0.469067,0.063816)
steals = Constant(0.013739,0.018139)
csRate = Constant(0.282805,0.304335)

LG_OUTCOMES = {
			'singles' : singles.mean,
			'doubles' : doubles.mean,
			'triples' : triples.mean,
			'homers' : homers.mean,
			'strikeouts' : strikeouts.mean,
			'walks' : walks.mean,
			'hbp' : hbp.mean,
			'inPlayOuts' : inPlayOuts.mean
		}

dpRate = 0.066844
outsFB = 0.394876
outsGB = 0.507380
outsLD = 0.097744
hitsFB = 0.246425
hitsGB = 0.323737
hitsLD = 0.429837