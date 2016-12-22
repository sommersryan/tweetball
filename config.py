
#dict of league avg event probabilities
#individual player attributes modify these? 

LG_AVG = {
	'outcomes' : {
		'1b' : 27538/184575,
		'2b' : 8255/184575,
		'3b' : 873/184575,
		'hr' : 5610/184575,
		'bb' : 15088/184575,
		'so' : 38982/184575,
		'hbp' : 1651/184575,
		'out' : 86578/184575
		},
	'conditionals' : {
		'sb' : 2536/184575,
		'csRate' : 1000/3536,
		'dpRate' : 3721/55667, #for ball in play with runners on
		'ldOut' : 8291/84824, #percentage of outs that are linedrives
		'fbOut' : 33495/84824,
		'gbOut' : 43038/84824,
		'ldHit' : 17947/41753, #percentage of hits that are linedrives
		'fbHit' : 10289/41753,
		'gbHit' : 13517/41753
		}
}
