from fractions import Fraction
import random

def tallyScore(game, pitcher):
	
	score = 0
	
	for key, value in scorecard.items():
		if key(pitcher = pitcher, game = game):
			score += value
	
	if score < 0:
		score = 0
	
	return score
	
def bullpenCall(game, pitcher):

	choice = random.randint(1, 100)
	score = tallyScore(game, pitcher)
	
	if choice > score:
		return False
		
	return True

def sixthOrLater(**kwargs):
	return kwargs['game'].inning >= 6 
	
def pitcherAllowedMoreThanFourRuns(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['R'] > 4
	
def pitcherAllowedMoreThanSixRuns(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['R'] > 6
	
def pitcherThrowingShutout(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['R'] == 0

def pitcherWalkedFiveOrMore(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['BB'] >= 5
	
def noHitter(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['H'] == 0
	
def pitcherThrownLessThanOneInning(**kwargs):
	return kwargs['pitcher'].pitchingGameStats['IP'] < Fraction(1,1)
	
scorecard = {
				sixthOrLater : 40,
				pitcherAllowedMoreThanFourRuns: 15,
				pitcherAllowedMoreThanSixRuns: 25,
				pitcherThrowingShutout: -25,
				noHitter: -100,
				pitcherThrownLessThanOneInning: -10,
				pitcherWalkedFiveOrMore: 15
			}