from tweet import api
from tweepy import Cursor
from datetime import datetime
from mongo_player_store import *
import time, roster

IDs = []

for page in Cursor(api.followers_ids, screen_name=api.me().screen_name).pages():
	IDs.extend(page)
	time.sleep(60)
	
currentPlayers = mongoGetAllTwitterIds()

addList = list(set(IDs) - set(currentPlayers))
removeList = list(set(currentPlayers) - set(IDs))

for addition in addList:

	player = roster.Player.fromTwitter(api.get_user(addition))
	
	record = playerMaptoMongo(player)
	
	record['lastStart'] = datetime.utcnow()
	
	mongoPlayerSave(record)
	
	player.notifyAttributes()
	time.sleep(120)
	
for removal in removeList:

	mongoDeleteByTwitterId(removal)
