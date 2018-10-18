import os
from urllib.parse import quote_plus

#PA time in seconds
PA_TIME = 102

#Number of PAs to tweet about per game
NUM_PAS = 15

#Possible outcomes of a plate appearance
RESULT_TYPES = ['single','double','triple','HR','strikeout','BB','HBP','inPlayOut','GDP','sacrifice','error']

#S3 Buckets
PLAYERS_BUCKET = os.environ.get('PLAYERS_BUCKET')
BOXSCORE_BUCKET = os.environ.get('BOXSCORE_BUCKET')

#Twitter and S3 keys
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID") or ''
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or ''

CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET') or ''
CONSUMER_KEY = os.environ.get('CONSUMER_KEY') or ''
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN') or ''
ACCESS_SECRET = os.environ.get('ACCESS_SECRET') or ''

CURRENT_SEASON = os.environ.get('CURRENT_SEASON') or '0'

MONGO_USER = os.environ.get('MONGO_USER')
MONGO_PASS = os.environ.get('MONGO_PASS')
MONGO_IP = os.environ.get('MONGO_IP')
MONGO_AUTH_SOURCE = os.environ.get('MONGO_AUTH_SOURCE')

MONGO_URI = "mongodb://{0}:{1}@{2}/?authSource={3}".format(quote_plus(MONGO_USER), quote_plus(MONGO_PASS), MONGO_IP, MONGO_AUTH_SOURCE)

PLAYER_SAVING_ENABLED = bool(int(os.environ.get('PLAYER_SAVING_ENABLED'))) or False