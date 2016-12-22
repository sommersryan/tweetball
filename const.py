import random

class Constant(object):
	def __init__(mean,stdDev):
		self.mean = mean
		self.stdDev = stdDev

singles = Constant(0.149197,0.032242)
doubles = Constant(0.044724,0.013545)
triples = Constant(0.004730,0.005326)
homers = Constant(0.030394,0.015656)
strikeouts = Constant(0.211199,0.061989)
walks = Constant(0.081744,0.03009)
hbp = Constant(0.008945,0.008299)
inPlayOuts = Constant(0.469067,0.063816)

