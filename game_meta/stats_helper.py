from datetime import datetime

PITCHING = 'pitcherId'
BATTING = 'batterId'

class StatsHelper(object):

    def __init__(self, api_instance):
        self.api = api_instance

    # methods for returning a dict of pitcher stats and a dict of batter stats I think, passing in player
    # and (somehow) scope (i.e. game or date range -- kind of where overload would be handy Maybe just
    # args for a date range and a game id and ignore one if the other is provided). Then smaller
    # methods would parse individual result counts out of query results?
    # listcomps will be key here -- reference that document that emulates linq queries with python

    def get_stats(self, player, player_mode, game_id = None, start_date: datetime = None, end_date: datetime = None):

