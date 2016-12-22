import random

def weightedChoice(choices):
	r = random.uniform(0, 1)
	upto = 0
	for c, w in choices.items():
		if upto + w >= r:
			return c
		upto += w