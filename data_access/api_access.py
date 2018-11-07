import requests
import os

auth = (os.getenv('API_USER'), os.getenv('API_PASSWORD'))
base_url = "http://{0}/".format(os.getenv('API_IP'))



