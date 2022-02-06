import random
from collections import Counter

import config
import datetime

from league import BAT_DIST, PITCH_DIST

from utils import percentile


class Ratings(object):

    def __init__(self, batting, pitching, **kwargs):
        self.contact = kwargs['contact']
        self.power = kwargs['power']
        self.discipline = kwargs['discipline']
        self.control = kwargs['control']
        self.stuff = kwargs['stuff']
        self.composure = kwargs['composure']
        self.batting = batting
        self.pitching = pitching

    @classmethod
    def new(cls):
        ratings = {
            rating: random.randint(1, 99) for rating in [
                'contact',
                'power',
                'discipline',
                'control',
                'stuff',
                'composure'
            ]
        }

        batting, pitching = generate_probabilities(ratings)

        rating_set = cls(batting, pitching, **ratings)

        return rating_set

    @classmethod
    def from_ratings(cls, **kwargs):
        batting, pitching = generate_probabilities(kwargs)

        return cls(batting, pitching, **kwargs)

    @classmethod
    def blank(cls):
        ratings = {
            rating: 0 for rating in [
                'contact',
                'power',
                'discipline',
                'control',
                'stuff',
                'composure'
            ]
        }

        batting = {}
        pitching = {}

        rating_set = cls(batting, pitching, **ratings)

        return rating_set


def generate_probabilities(ratings_dict):
    batting, pitching = {}, {}

    batting['single'] = percentile(ratings_dict['contact'], BAT_DIST['single'])
    batting['strikeout'] = percentile((100 - ratings_dict['contact']), BAT_DIST['strikeout'])
    batting['double'] = percentile(ratings_dict['power'], BAT_DIST['double'])
    batting['triple'] = percentile(ratings_dict['power'], BAT_DIST['triple'])
    batting['HR'] = percentile(ratings_dict['power'], BAT_DIST['HR'])
    batting['inPlayOut'] = percentile((100 - ratings_dict['power']), BAT_DIST['inPlayOut'])
    batting['BB'] = percentile(ratings_dict['discipline'], BAT_DIST['BB'])
    batting['HBP'] = percentile(ratings_dict['discipline'], BAT_DIST['HBP'])
    batting['sacrifice'] = percentile(random.randint(1, 99), BAT_DIST['sacrifice'])
    batting['GDP'] = percentile(random.randint(1, 99), BAT_DIST['GDP'])
    batting['error'] = percentile(random.randint(1, 99), BAT_DIST['error'])

    pitching['single'] = percentile((100 - ratings_dict['stuff']), PITCH_DIST['single'])
    pitching['strikeout'] = percentile(ratings_dict['stuff'], PITCH_DIST['strikeout'])
    pitching['double'] = percentile((100 - ratings_dict['control']), PITCH_DIST['double'])
    pitching['triple'] = percentile((100 - ratings_dict['control']), PITCH_DIST['triple'])
    pitching['HR'] = percentile((100 - ratings_dict['control']), PITCH_DIST['HR'])
    pitching['inPlayOut'] = percentile(ratings_dict['stuff'], PITCH_DIST['inPlayOut'])
    pitching['BB'] = percentile((100 - ratings_dict['control']), PITCH_DIST['BB'])
    pitching['HBP'] = percentile((100 - ratings_dict['control']), PITCH_DIST['HBP'])
    pitching['sacrifice'] = percentile(random.randint(1, 99), PITCH_DIST['sacrifice'])
    pitching['GDP'] = percentile(ratings_dict['composure'], PITCH_DIST['GDP'])
    pitching['error'] = percentile(random.randint(1, 99), PITCH_DIST['error'])

    return batting, pitching


class Player(object):

    def __init__(self, id, name, fullName, handle, handedness,
                 uniNumber, ratings, pitchingGameStats, battingGameStats,
                 active, sub, position):

        self.id = id
        self.name = name
        self.fullName = fullName
        self.handle = handle
        self.handedness = handedness
        self.uniNumber = uniNumber
        self.ratings = ratings
        self.pitchingGameStats = pitchingGameStats
        self.battingGameStats = battingGameStats
        self.active = active
        self.sub = sub
        self.position = position

    @classmethod
    def from_dict(cls, **kwargs):
        base_ratings = kwargs.pop('ratings')
        rating_set = Ratings.from_ratings(**base_ratings)

        kwargs['ratings'] = rating_set
        kwargs['active'] = True

        kwargs['pitchingGameStats'] = Counter()
        kwargs['battingGameStats'] = Counter()

        return cls(**kwargs)

    def __repr__(self):

        return "<Player {0}>".format(self.name)

    def __str__(self):

        return self.handle


class Lineup(object):

    def __init__(self, battingOrder, pitchers):

        self.battingOrder = battingOrder
        self.pitchers = pitchers
        self.pitchers.insert(0, random.choice(battingOrder))
        self.currentPitcher = pitchers.pop(0)
        self.usedPitchers = [self.currentPitcher, ]
        self.atBat = 0
        self.onDeck = 1
        self.assignPositions()

    def newBatter(self):

        isActive = False

        while not isActive:

            try:
                nb = self.battingOrder[self.onDeck]
                self.onDeck += 1

            except IndexError:
                nb = self.battingOrder[0]
                self.onDeck = 1

            isActive = nb.active

        return nb

    def assignPositions(self):

        positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
        random.shuffle(positions)

        for player in self.battingOrder:
            if len(positions) < 1:
                player.position = None
                continue

            if player == self.currentPitcher:
                player.position = 'P'

            else:
                player.position = positions.pop()

        return True

    def subPitcher(self, previousPA):

        if self.pitchers:
            self.currentPitcher.active = False
            substitute = self.pitchers.pop(0)
            substitute.sub = True
            substitute.position = 'P'

            new_timestamp = previousPA.timestamp + datetime.timedelta(seconds=(config.PA_TIME / 2))

            subInfo = Substitution(self.currentPitcher, substitute, previousPA, True, new_timestamp)

            self.battingOrder.insert(self.battingOrder.index(self.currentPitcher) + 1, substitute)
            self.currentPitcher = substitute
            self.usedPitchers += [self.currentPitcher]

            return subInfo

        return False


class Team(object):

    def __init__(self, team_id, nickname, location, lineup):
        self.nickname = nickname
        self.location = location
        self.lineup = lineup
        self.team_id = team_id

    @classmethod
    def from_dict(cls, **kwargs):
        batters = [Player.from_dict(**p) for p in kwargs['lineup']['battingOrder']]
        pitchers = [Player.from_dict(**p) for p in kwargs['lineup']['pitchers']]

        lineup = Lineup(batters, pitchers)

        kwargs['lineup'] = lineup

        return cls(**kwargs)

    def __str__(self):
        return "{0} {1}".format(self.location, self.nickname)


class Substitution(object):

    def __init__(self, playerOut, playerIn, previousPA, isPitchingChange, timestamp):

        self.top = previousPA.top
        self.inning = previousPA.inning
        self.outs = previousPA.endState.outs
        self.runs = 0
        self.isPitchingChange = isPitchingChange
        self.wpa = 0
        self.playerOut = playerOut
        self.playerIn = playerIn
        self.isSubstitution = True
        self.timestamp = timestamp

        self.narratives = [str(self)]

    def __str__(self):

        if self.isPitchingChange:
            subString = "{0} enters the game to pitch, replacing {1}.".format(self.playerIn.handle,
                                                                              self.playerOut.handle)

        else:
            subString = "{0} enters the game to pinch hit for {1}.".format(self.playerIn.handle, self.playerOut.handle)

        return subString
