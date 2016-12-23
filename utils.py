import random

def weightedChoice(choices):
	total = sum(list(choices.values()))
	r = random.uniform(0, total)
	upto = 0
	for c, w in choices.items():
		if upto + w >= r:
			return c
		upto += w
		
def log5(pitcherValue, hitterValue, leagueValue):
	#Bill James' log 5 method of predicting hitter/pitcher matchup outcome
	
	num = (hitterValue * pitcherValue) / leagueValue
	
	denom = num + (( (1 - hitterValue) * (1 - pitcherValue) ) / (1 - leagueValue) )
	
	return num / denom