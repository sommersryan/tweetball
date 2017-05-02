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

def percentile(p, data):
	#finds the pth percentile in the set data
	
	ord = (p / 100) * len(data)
	
	return data[int(ord)]
	
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

emojis = {	'top' : '\U0001F53C',
			'bottom' : '\U0001F53D',
			'empty' : '\U0000002A\U0000FE0F\U000020E3',
			'first' : '\U00000031\U0000FE0F\U000020E3',
			'second' : '\U00000032\U0000FE0F\U000020E3',
			'third' : '\U00000033\U0000FE0F\U000020E3',
			'out' : '\U000026AB',
			'noOut' : '\U000026AA'
			}