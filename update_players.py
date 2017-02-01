from tweet import api
from tweepy import Cursor
from storage import playerStore
import time, roster

IDs = []

for page in Cursor(api.followers_ids, screen_name=api.me().screen_name).pages():
	IDs.extend(page)
	time.sleep(60)
	
currentPlayers = [int(a.key) for a in list(playerStore.list())]

addList = list(set(IDs) - set(currentPlayers))
removeList = list(set(currentPlayers) - set(IDs))

for addition in addList:

	player = roster.Player(api.get_user(addition))
	player.save()
	player.notifyAttributes()
	time.sleep(120)
	
for removal in removeList:

	playerStore.delete_key(removal)
