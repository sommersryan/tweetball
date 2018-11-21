import requests, os

auth = (os.getenv('API_USER'), os.getenv('API_PASSWORD'))
base_url = "http://{0}/".format(os.getenv('API_IP'))
headers = {'Content-type': 'application/json'}

class API(object):

	def get_player_by_id(self, objectId):

		req = requests.get("{0}/players/{1}".format(base_url, objectId), auth=auth)
		
		return req.text
		
	def get_player_by_handle(self, handle):
	
		req = requests.get("{0}/players/{1}".format(base_url, handle), auth=auth)
		
		return req.text
		
	def get_players(self, sort_key = None, desc=False, count = None, page = 1):
		
		if desc:
			sort_key = "-{0}".format(sort_key)
		
		req = requests.get("{0}/players?sort={1}&max_results={2}&page={3}"
			.format(base_url, sort_key, count, page), auth=auth)
			
		return req.text
		
	def post_event(self, event_json):
	
		req = requests.post("{0}/events".format(base_url), 
			auth=auth, headers=headers, data=event_json)
		
		return req.text
		
	def put_game(self, game_json):
	
		req = requests.put("{0}/games".format(base_url),
			auth=auth, headers=headers, data=game_json)
			
		return req.text
		
	

