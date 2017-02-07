import os

#Base advancements -- number of times out of 100 the named advancement occurs
AD_RATES = {
			SINGLE_1ST_TO_2ND = 70
			SINGLE_1ST_TO_3RD = 30
			#
			SINGLE_2ND_TO_3RD = 35
			SINGLE_2ND_SCORES = 65
			#
			DOUBLE_1ST_TO_3RD = 60
			DOUBLE_1ST_SCORES = 40
			}

#PA time in seconds
PA_TIME = 134

#Number of PAs to tweet about per game
NUM_PAS = 20

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