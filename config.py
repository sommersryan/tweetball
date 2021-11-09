import os

# PA time in seconds
PA_TIME = 115

# Number of PAs to tweet about per game
NUM_PAS = 18

# Possible outcomes of a plate appearance
RESULT_TYPES = ['single', 'double', 'triple', 'HR', 'strikeout', 'BB', 'HBP', 'inPlayOut', 'GDP', 'sacrifice', 'error']

# messaging
AMQP_URL = os.environ.get('AMQP_URL')
