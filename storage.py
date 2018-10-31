from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import PLAYERS_BUCKET, BOXSCORE_BUCKET
import random, pickle

storageConnection = S3Connection()
boxScoreBucket = storageConnection.get_bucket(BOXSCORE_BUCKET)