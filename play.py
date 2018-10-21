import random, datetime, config
from utils import baseNarratives, transitions, log5, weightedChoice, emojis
from league import leagueMeans
from tweet import api
from wpa import winProb
from fractions import Fraction

class Matchup(object):

	def __init__(self, batting, pitching):
		
		lgAvg = leagueMeans()
		
		for key in config.RESULT_TYPES:
		
			resultProb = log5(pitching[key], batting[key], lgAvg[key])
			
			setattr(self, key, resultProb)
			
	def genResult(self):
	
		return weightedChoice(self.__dict__)
		

class Event(object):

	def __init__(self, type):
	
		self.type = type
		self.narrative = self.genString()
		
		if type in ['strikeout', 'inPlayOut', 'sacrifice', 'GDP']:
			self.batterOut = True
			
		else:
			self.batterOut = False
			
		if type in ['single', 'double', 'triple', 'HR']:
			self.isHit = True
			
		else:
			self.isHit = False
			
		if type in ['BB', 'HBP', 'sacrifice']:
			self.isAB = False
			
		else:
			self.isAB = True

	def genString(self):
		
		outfield = ['left', 'center', 'right']
		infield = ['first', 'second', 'third', 'shortstop']
		
		outs = [
					"lines out to {0}".format(random.choice(infield + outfield)),
					"flies out to {0}".format(random.choice(outfield)),
					"grounds out to {0}".format(random.choice(infield))
				]
				
		strings = {
					'strikeout' : 'strikes out',
					'sacrifice' : 'sacrifices',
					'GDP' : 'grounds into double play',
					'inPlayOut' : random.choice(outs),
					'single' : "singles to {0}".format(random.choice(outfield)),
					'double' : "doubles to {0}".format(random.choice(outfield)),
					'triple' : "triples to {0}".format(random.choice(outfield)),
					'HR' : "homers to {0}".format(random.choice(outfield)),
					'HBP' : "is hit by pitch",
					'BB' : "walks",
					'error' : "reaches on error"
				}
				
		return strings[self.type]
					
class BaseOutState(object):

	def __init__(self, first=None, second=None, third=None, outs=0):
	
		self.first = first
		self.second = second
		self.third = third
		self.outs = outs
	
	def getState(self):
		
		firstBase, secondBase, thirdBase = '', '', ''
		
		if self.first:
			firstBase = '1'
			
		if self.second:
			secondBase = '2'
			
		if self.third:
			thirdBase = '3'
			
		state = '{0}{1}{2}'.format(firstBase, secondBase, thirdBase)
		
		if state == '':
			state = '0'
		
		return (int(state), self.outs)
			
	def __str__(self):
		
		narr = baseNarratives[self.getState()[0]]
		
		return "{0} and {1} outs".format(narr, self.outs)
	
	def queue(self):
	
		runners = []
		
		for runner in [self.first, self.second, self.third]:
		
			if runner:
			
				runners.append(runner)
				
		return runners
		
class PlateAppearance(object):
	
	def __init__(self, top, inning, awayScore, homeScore, baseState, batter, pitcher):
		
		self.top = top
		self.inning = inning
		self.awayScore = awayScore
		self.homeScore = homeScore
		self.baseState = baseState
		self.batter = batter
		self.pitcher = pitcher
		self.narratives = []
		
		if baseState.outs == 3:
			self.transitions = [None,]
		
		else:
			self.transitions = transitions[baseState.getState()]
			
		self.matchup = Matchup(batter.ratings.batting, pitcher.ratings.pitching)
		
		choice = False
		
		while not choice:
			
			ev = self.matchup.genResult()
			states = random.sample(self.transitions, len(self.transitions))
			
			for i in states: 
				
				if ev in i[1]:
				
					self.event = Event(ev)
					endBases = i[0]
					self.runs = i[2]
					choice = True
					break
		
		self.narratives.append("{0} {1}".format(self.batter.handle, self.event.narrative))
		
		self.endState = self.advanceRunners(endBases, self.runs)
		
		self.wpa = self.getWPA()
		
		self.batter.battingGameStats[self.event.type] += 1
		self.pitcher.pitchingGameStats[self.event.type] += 1
		
		if self.event.type in ['single', 'double', 'triple', 'HR']:
			self.batter.battingGameStats['H'] +=1
			self.pitcher.pitchingGameStats['H'] +=1
		
		if self.event.type not in ['BB', 'HBP', 'sacrifice']:
			self.batter.battingGameStats['AB'] += 1
			
		self.batter.battingGameStats['PA'] += 1
		self.pitcher.pitchingGameStats['BF'] += 1
		
		self.batter.battingGameStats['RBI'] += self.runs
		self.pitcher.pitchingGameStats['R'] += self.runs
		
		if self.event.type == 'GDP':
			self.pitcher.pitchingGameStats['IP'] += Fraction(2,3)
		
		elif self.endState.outs != self.baseState.outs:
			self.pitcher.pitchingGameStats['IP'] += Fraction(1,3)
			
		self.batter.battingGameStats['WPA'] += self.wpa
		self.pitcher.pitchingGameStats['WPA'] += -self.wpa
		
	def advanceRunners(self, newBases, runs):
		
		oldState = self.baseState
		newState = BaseOutState()
		newState.outs = newBases[1]
		runners = oldState.queue()
		
		runners.insert(0, self.batter)
		
		for i in range(0, runs):
			
			self.narratives += ["{0} scores".format(str(runners.pop()))]
		
		if len(runners) > 0:
		
			if '3' in str(newBases[0]):
			
				newState.third = runners.pop()
				
				if newState.third != oldState.third:
					self.narratives += ["{0} to third".format(str(newState.third))]
				
		if len(runners) > 0:
		
			if '2' in str(newBases[0]):
			
				newState.second = runners.pop()
				
				if newState.second != oldState.second:
					self.narratives += ["{0} to second".format(str(newState.second))]
				
		if len(runners) > 0:
		
			if '1' in str(newBases[0]):
			
				newState.first = runners.pop()	

		if self.event.batterOut:
			try: 
				runners.pop()
			except IndexError:
				print(oldState)
				print(newBases)
				print(oldState.queue())
				
		return newState

	def getWPA(self):
	
		if self.top:
			startDiff = self.awayScore - self.homeScore
			endDiff = ((self.awayScore + self.runs) - self.homeScore)
			team = "V"
			
		else:
			startDiff = self.homeScore - self.awayScore
			endDiff = ((self.homeScore + self.runs) - self.awayScore)
			team = "H"
			
		if startDiff > 6:
			startDiff = 6
			
		if startDiff < -6:
			startDiff = -6
			
		if endDiff > 6:
			endDiff = 6
			
		if endDiff < -6:
			endDiff = -6
		
		if self.inning > 9:
			inn = 9
			
		else:
			inn = self.inning
		
		startState = (team, inn, *self.baseState.getState(), startDiff)
		startWP = winProb[startState]
		
		if self.endState.outs == 3:
		
			if self.top:
				team = "H"
				inn = self.inning
				
			else:
				team = "V"
				inn = self.inning + 1
			
			if inn > 9:
				inn = 9
			
			bases = BaseOutState()
			diff = -endDiff
			
			endState = (team, inn, *bases.getState(), diff)
			endWP = 1 - winProb[endState]
		
		else:
			
			endState = (team, inn, *self.endState.getState(), endDiff)
			
			try:
				endWP = winProb[endState]
			
			except KeyError:
				endWP = 1
			
		return endWP - startWP
		
	def tweetPA(self, replyTo):
	
		if self.top:
			half = emojis['top']
			aAfterScore = self.awayScore + self.runs
			hAfterScore = self.homeScore
			
		else:
			half = emojis['bottom']
			aAfterScore = self.awayScore
			hAfterScore = self.homeScore + self.runs
			
		inningString = "{0}{1}".format(half, self.inning)
		baseString = ""
		
		if self.baseState.first:
			baseString += emojis['first']
			
		else:
			baseString += emojis['empty']
			
		if self.baseState.second:
			baseString += emojis['second']
		
		else:
			baseString += emojis['empty']
			
		if self.baseState.third:
			baseString += emojis['third']
			
		else:
			baseString += emojis['empty']
		
		outString = emojis['out'] * self.baseState.outs
		outString += emojis['noOut'] * (2 - self.baseState.outs)
		
		narrative = str(self)
		
		if self.runs > 0:
			if self.top:
				afterScoreString = "{0} -- {1}".format(aAfterScore, hAfterScore)
			else:
				afterScoreString = "{0} -- {1}".format(hAfterScore, aAfterScore)
		else:
			afterScoreString = ""
				
		if self.top:
			beforeScoreString = "{0} -- {1}".format(self.awayScore, self.homeScore)
		else:
			beforeScoreString = "{0} -- {1}".format(self.homeScore, self.awayScore)
		
		t = "{0} | {1} | {2} | {3}|\r\n {4}. {5}".format(inningString, beforeScoreString, baseString, outString, narrative, afterScoreString)
		
		if len(t) > 260:
			t = t[:260]
		
		tweetID = api.update_status(t, in_reply_to_status_id = replyTo).id
		
		return tweetID
	
	def __str__(self):
	
		description = '. '.join(self.narratives)
		
		return "{0}".format(description)
	
class Game(object):

	def __init__(self, homeTeam, awayTeam):
	
		self.homeTeam = homeTeam
		self.awayTeam = awayTeam
		self.homeScore = 0
		self.awayScore = 0
		self.PAs = []
		self.inning = 1
		self.top = True
		self.startTime = datetime.datetime.now()
		self.complete = False
		
	def iterate(self, currentPA):
	
		self.PAs.append(currentPA)
		
		if self.top:
		
			self.awayScore += currentPA.runs
			batter = self.awayTeam.lineup.newBatter()
			pitcher = self.homeTeam.lineup.currentPitcher
			
			return PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, currentPA.endState, batter, pitcher)
			
		elif not self.top:
		
			self.homeScore += currentPA.runs
			
			if self.inning >= 9 and self.homeScore > self.awayScore:
			
				return False
			
			batter = self.homeTeam.lineup.newBatter()
			pitcher = self.awayTeam.lineup.currentPitcher
			
			return PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, currentPA.endState, batter, pitcher)
			
	def playInning(self):
		
		if self.inning >= 10 and self.top:
		
			if self.awayScore > self.homeScore:
			
				self.complete = True
				return True
		
		if self.inning == 9 and not self.top:
		
			if self.homeScore > self.awayScore:
			
				self.complete = True
				return True
		
		if self.top:
			
			if self.inning >= 6 and self.homeTeam.lineup.currentPitcher.pitchingGameStats['WPA'] < 0 and random.randint(0,100) > 50:
				
				self.homeTeam.lineup.subPitcher()
			
			if self.inning == 1:
				batter = self.awayTeam.lineup.battingOrder[0]
			else:
				batter = self.awayTeam.lineup.newBatter()
			
			pitcher = self.homeTeam.lineup.currentPitcher
		
		elif not self.top:
			
			if self.inning >=6 and self.awayTeam.lineup.currentPitcher.pitchingGameStats['WPA'] < 0 and random.randint(0,100) > 50:
			
				self.awayTeam.lineup.subPitcher()
			
			if self.inning == 1:
				batter = self.homeTeam.lineup.battingOrder[0]
			else:	
				batter = self.homeTeam.lineup.newBatter()
			
			pitcher = self.awayTeam.lineup.currentPitcher
		
		currentPA = PlateAppearance(self.top, self.inning, self.awayScore, self.homeScore, BaseOutState(), batter, pitcher)
		
		while True:
		
			currentPA = self.iterate(currentPA)
			
			if not currentPA:
			
					self.complete = True
					return True
			
			if currentPA.endState.outs == 3:
				
				self.PAs.append(currentPA)
				
				if not self.top:
					self.inning += 1
					self.top = not self.top
					
				elif self.top:
					self.top = not self.top
					
				return True
				
	def play(self):
		
		while not self.complete:
			self.playInning()
	
	def tearDown(self):
	
		# for player in self.homeTeam.lineup.battingOrder:
			# player.save()
			
		# for player in self.awayTeam.lineup.battingOrder:
			# player.save()
			
		# for player in self.homeTeam.lineup.usedPitchers:
			# player.save()
			
		# for player in self.awayTeam.lineup.usedPitchers:
			# player.save()
			
		for player in set(self.homeTeam.lineup.battingOrder 
				+ self.awayTeam.lineup.battingOrder + self.homeTeam.lineup.usedPitchers 
				+ self.awayTeam.lineup.usedPitchers):
			player.save()
			
		return True
	
	def gameLog(self):
	
		for i in self.PAs:
		
			print('Top ' if i.top else 'Bot ', i.inning, " | ", i)
			
		return True
