from random import random
from bisect import bisect

def weightedChoice(choices):
	values, weights = list(choices.keys()), list(choices.values())
	total = 0
	cumulative_weights = []
	
	for w in weights:
		total += w
		cumulative_weights.append(total)
		
	x = random() * total
	i = bisect(cumulative_weights, x)
	
	return values[i]
		
def log5(pitcherValue, hitterValue, leagueValue):
	#Bill James' log 5 method of predicting hitter/pitcher matchup outcome
	
	num = (hitterValue * pitcherValue) / leagueValue
	
	denom = num + (( (1 - hitterValue) * (1 - pitcherValue) ) / (1 - leagueValue) )
	
	return num / denom
	
baseNarratives = {
					0 : 'bases empty',
					1 : 'runner on first',
					2 : 'runner on second',
					3 : 'runner on third',
					12 : 'runners on first and second',
					13 : 'runners on first and third',
					23 : 'runners on second and third',
					123 : 'bases loaded'
				}