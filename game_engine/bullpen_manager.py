from fractions import Fraction
import random

def tallyScore(game, pitcher):

	pitcher_stats = game.statsHelper.get_stats(pitcher._id, 'pitcherId', game_id=game._id)

	score = 0
	
	for key, value in scorecard.items():
		if key(pitcher=pitcher, game=game, pitcher_stats=pitcher_stats):
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
	return kwargs['pitcher_stats']['R'] > 4
	
def pitcherAllowedMoreThanSixRuns(**kwargs):
	return kwargs['pitcher_stats']['R'] > 6
	
def starterAllowedLessThanFourRuns(**kwargs):

	if kwargs['pitcher'].sub:
		return False

	return kwargs['pitcher_stats']['R'] < 4
	
def relieverAllowedMoreThanTwoRuns(**kwargs):

	if kwargs['pitcher'].sub:
		return kwargs['pitcher_stats']['R'] > 2
		
	return False
	
def pitcherThrowingShutout(**kwargs):
	return kwargs['pitcher_stats']['R'] == 0

def pitcherWalkedFiveOrMore(**kwargs):
	return kwargs['pitcher_stats']['BB'] >= 5
	
def noHitter(**kwargs):
	return kwargs['pitcher_stats']['H'] == 0
	
def pitcherThrownLessThanOneInning(**kwargs):
	return kwargs['pitcher_stats']['IP'] < Fraction(1, 1)
	
def pitcherRAGreaterThanEight(**kwargs):
	
	pitcherStats = kwargs['pitcher_stats']
	
	if pitcherStats['IP'] == 0:
		if pitcherStats['R'] > 2:
			return True
		else:
			return False
			
	RA = (pitcherStats['R'] / float(pitcherStats['IP'])) * 9
	
	return RA > 8

def pitcherFacedMoreThanThirtyBatters(**kwargs):
	return kwargs['pitcher_stats']['BF'] > 30
		
scorecard = {
				sixthOrLater : 25,
				pitcherAllowedMoreThanFourRuns: 30,
				pitcherAllowedMoreThanSixRuns: 80,
				pitcherRAGreaterThanEight: 50,
				pitcherThrowingShutout: -80,
				noHitter: -100,
				pitcherThrownLessThanOneInning: -10,
				pitcherWalkedFiveOrMore: 25,
				starterAllowedLessThanFourRuns: -60,
				relieverAllowedMoreThanTwoRuns: 30,
				pitcherFacedMoreThanThirtyBatters: 45
			}