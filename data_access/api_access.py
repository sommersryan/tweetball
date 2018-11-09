import requests, os

auth = (os.getenv('API_USER'), os.getenv('API_PASSWORD'))
base_url = "http://{0}/".format(os.getenv('API_IP'))

class API(object):

	def get_player_by_id(self, objectId):

		req = requests.get("{0}/players/{1}".format(base_url, objectId), auth=auth)
		
		return req.text
		
	def get_player_by_handle(self, handle):
	
		req = requests.get("{0}/players/{1}".format(base_url, handle), auth=auth)
		
		return req.text
		
	

