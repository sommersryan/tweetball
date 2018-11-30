from datetime import datetime
from collections import Counter
from fractions import Fraction
import json

PITCHING = 'pitcherId'
BATTING = 'batterId'
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


class StatsHelper(object):

	def __init__(self, api_instance):
		self.api = api_instance

	def get_stats(self, player_id, player_mode, game_id=None, start_date: datetime = None, end_date: datetime = None):

		raw_events = json.loads(self.api.get_player_events(player_id))['_items']

		filtered_events = [a for a in raw_events if a[player_mode] == player_id]

		if game_id:
			final_events = [a for a in filtered_events if a['game_id'] == game_id]
		else:
			final_events = [a for a in filtered_events if
							start_date < datetime.strptime(a['timestamp'], TIME_FORMAT) < end_date]

		stats = self.count_events(final_events, player_mode)

		return stats

	def count_events(self, events_list, player_mode):

		counter = Counter()

		for event in events_list:
			counter[event['event']['type']] += 1

		counter['H'] = len([a for a in events_list if a['event']['isHit']])

		if player_mode == PITCHING:
			counter['BF'] = len(events_list)
			counter['R'] = sum([a['runs'] for a in events_list])
			counter['WPA'] = -sum([a['wpa'] for a in events_list])
			counter['IP'] = Fraction(sum([a['endState']['outs'] - a['baseState']['outs'] for a in events_list]), 3)
		else:
			counter['RBI'] = sum([a['runs'] for a in events_list])
			counter['PA'] = len(events_list)
			counter['WPA'] = sum([a['wpa'] for a in events_list])
			counter['AB'] = len([a for a in events_list if a['event']['isAB']])

		return counter
