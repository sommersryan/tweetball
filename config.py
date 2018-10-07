import os

#PA time in seconds
PA_TIME = 90

#Number of PAs to tweet about per game
NUM_PAS = 15

#Possible outcomes of a plate appearance
RESULT_TYPES = ['single','double','triple','HR','strikeout','BB','HBP','inPlayOut','GDP','sacrifice','error']

#Twitter accounts for testing use
TEST_ACCOUNTS = ['FoodNetwork', 'WWENetwork', 'nflnetwork', 'OnionSports', 'CNN', 'FoxNews', 'maddow', 'MSNBC', 'AV_Newswire']

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
