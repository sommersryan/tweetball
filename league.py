import random, config
from statistics import mean

BAT_AVG_OUTCOMES = {
					'HR' : {
								'hi' : .070,
								'lo' : .001,
								'mean' : .027,
								'sd' : .020
							},
					'triple' : {
								'hi' : .032,
								'lo' : .001,
								'mean' : .005,
								'sd' : .005 
							},
					'double' : {
								'hi' : .081,
								'lo' : .011,
								'mean' : .045,
								'sd' : .011
							},
					'single' : {
								'hi' : .260,
								'lo' : .080,
								'mean' : .152,
								'sd' : .030
							},
					'BB' : {
								'hi' : .206,
								'lo' : .020,
								'mean' : .078,
								'sd' : .030
							},
					'HBP' : {
								'hi' : .058,
								'mean' : .009,
								'lo' : .001,
								'sd' : .007
							},
					'inPlayOut' : {
									'hi' : .585,
									'mean' : .442,
									'lo' : .299,
									'sd' : .056
								},
					'strikeout' : {
									'hi' : .360,
									'mean' : .206,
									'lo' : .070,
									'sd' : .060
								},
					'sacrifice' : {
									'hi' : .045,
									'mean' : .006,
									'lo' : .001,
									'sd' : .005
								},
					'GDP' : {
								'hi' : .045,
								'mean' : .020,
								'lo' : .001,
								'sd' : .009
							},
					'error' : {
								'hi' : .010,
								'mean' : .005,
								'lo' : .001,
								'sd' : .001
							}
				}

PITCH_AVG_OUTCOMES = {
					'HR' : {
								'hi' : .052,
								'lo' : .007,
								'mean' : .027,
								'sd' : .008
							},
					'triple' : {
								'hi' : .016,
								'lo' : .001,
								'mean' : .005,
								'sd' : .002 
							},
					'double' : {
								'hi' : .070,
								'lo' : .023,
								'mean' : .045,
								'sd' : .009
							},
					'single' : {
								'hi' : .210,
								'lo' : .100,
								'mean' : .152,
								'sd' : .019
							},
					'BB' : {
								'hi' : .139,
								'lo' : .018,
								'mean' : .071,
								'sd' : .019
							},
					'HBP' : {
								'hi' : .029,
								'mean' : .008,
								'lo' : .001,
								'sd' : .004
							},
					'inPlayOut' : {
									'hi' : .579,
									'mean' : .486,
									'lo' : .369,
									'sd' : .034
								},
					'strikeout' : {
									'hi' : .343,
									'mean' : .203,
									'lo' : .104,
									'sd' : .043
								},
					'sacrifice' : {
									'hi' : .029,
									'mean' : .008,
									'lo' : .001,
									'sd' : .004
								},
					'GDP' : {
								'hi' : .045,
								'mean' : .020,
								'lo' : .001,
								'sd' : .007
							},
					'error' : {
								'hi' : .010,
								'mean' : .005,
								'lo' : .001,
								'sd' : .001
							}
				}				

def leagueMeans():
	
	means = {}
	
	for key in config.RESULT_TYPES:
	
		means.update({ key : mean([BAT_AVG_OUTCOMES[key]['mean'], PITCH_AVG_OUTCOMES[key]['mean']])})
	
	return means

def makeDist(outcomes):

	dists = {}
	
	for key, value in outcomes.items():

		k = key
		v = []
	
		for i in range(0,100000):
			
			while True:
				
				pick = random.gauss(value['mean'], value['sd'])
				
				if value['lo'] <= pick <= value['hi']:
					break
				
			v.append(pick)

		v.sort()
		dists.update({k : v})
	
	return dists
	
BAT_DIST = makeDist(BAT_AVG_OUTCOMES)
PITCH_DIST = makeDist(PITCH_AVG_OUTCOMES)