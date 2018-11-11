import pymongo
import json
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, CURRENT_SEASON
from fractions import Fraction
from collections import Counter

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]