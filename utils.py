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
				
transitions = {
					(0,0) : [
								((0,0),['HR',],1),
								((1,0),['BB','HBP','single','error'],0),
								((2,0),['double',],0),
								((3,0),['triple',],0),
								((0,1),['inPlayOut','strikeout'],0)
							],
					(1,0) : [
								((0,0),['HR',],2),
								((3,0),['triple',],1),
								((12,0),['BB','HBP','single','error'],0),
								((23,0),['double',],0),
								((1,1),['inPlayOut','strikeout'],0),
								((0,2),['GDP',],0)
							],
					(2,0) : [
								((0,0),['HR',],2),
								((1,0),['single','error',],1),
								((2,0),['double',],1),
								((3,0),['triple',],1),
								((12,0),['BB','HBP',],0),
								((2,1),['inPlayOut','strikeout',],0),
								((3,1),['sacrifice',],0),
								((0,2),['GDP',],0)
							],
					(3,0) : [
								((0,0),['HR',],2),
								((1,0),['single','error',],1),
								((2,0),['double',],1),
								((3,0),['triple',],1),
								((13,0),['BB','HBP',],0),
								((0,1),['sacrifice',],1),
								((3,1),['inPlayOut','strikeout',],0),
								((0,2),['GDP',],0)
							],
					(12,0) : [
								((0,0),['HR',],3),
								((3,0),['triple',],2),
								((12,0),['single','error',],0),
								((23,0),['double',],1),
								((123,0),['BB','HBP',],0),
								((12,1),['inPlayOut','strikeout',],0),
								((2,2),['GDP',],0),
								((3,2),['GDP',],0)
							],
					(13,0) : [
								((0,0),['HR',],3),
								((3,0),['triple',],2),
								((12,0),['single','error',],1),
								((23,0),['double',],1),
								((123,0),['BB','HBP',],0),
								((1,1),['sacrifice',],0),
								((13,1),['strikeout',],0),
								((0,2),['GDP',],1),
								((1,2),['GDP',],1),
								((2,2),['GDP',],1)
							],
					(23,0) : [
								((0,0),['HR',],3),
								((1,0),['single','error',],2),
								((2,0),['double',],2),
								((3,0),['triple',],2),
								((123,0),['BB','HBP',],0),
								((13,1),['sacrifice',],1),
								((23,1),['strikeout',],0)
							],
					(123,0) : [
								((0,0),['HR',],4),
								((3,0),['triple',],3),
								((12,0),['single','error',],2),
								((23,0),['double',],2),
								((123,0),['BB','HBP',],1),
								((12,1),['sacrifice',],1),
								((123,1),['inPlayOut',],0),
								((3,2),['GDP',],1)
							]
				}