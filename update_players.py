from tweet import api
from tweepy import Cursor
from storage import playerStore
import time

IDs = []

for page in Cursor(api.followers_ids, screen_name=api.me().screen_name).pages():
	IDs.extend(page)
	time.sleep(60)
	
currentPlayers = [int(a.key) for a in list(playerStore.list())]

addList = list(set(IDs) - set(currentPlayers))
removeList = list(set(currentPlayers) - set(IDs))

