import random

AVG_OUTCOMES = {
					'HR' : {
								'hi' : 70,
								'lo' : 1,
								'mean' : 27,
								'sd' : 20
							},
					'triple' : {
								'hi' : 32,
								'lo' : 1,
								'mean' : 5,
								'sd' : 5 
							},
					'double' : {
								'hi' : 81,
								'lo' : 11,
								'mean' : 45,
								'sd' : 11
							},
					'single' : {
								'hi' : 260,
								'lo' : 80,
								'mean' : 152,
								'sd' : 30
							},
					'BB' : {
								'hi' : 206,
								'lo' : 20,
								'mean' : 78,
								'sd' : 30
							},
					'HBP' : {
								'hi' : 58,
								'mean' : 9,
								'lo' : 1,
								'sd' : 7
							},
					'inPlayOut' : {
									'hi' : 585,
									'mean' : 442,
									'lo' : 299,
									'sd' : 56
								},
					'strikeout' : {
									'hi' : 360,
									'mean' : 206,
									'lo' : 70,
									'sd' : 60
								},
					'sacrifice' : {
									'hi' : 45,
									'mean' : 6,
									'lo' : 0,
									'sd' : 5
								},
					'GDP' : {
								'hi' : 45,
								'mean' : 20,
								'lo' : 1,
								'sd' : 9
							},
					'error' : {
								'hi' : 10,
								'mean' : 10,
								'lo' : 10,
								'sd' : 1
							}
				}
				
dists = {}

for key, value in AVG_OUTCOMES.items():

	k = key
	v= []
	
	for i in range(0,100000):
		
		v.append(round(random.gauss(value['mean'], value['sd'])))
	
	v.sort()
	dists.update({k : v})