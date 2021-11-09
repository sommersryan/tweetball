import pymongo
import json
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, CURRENT_SEASON
from fractions import Fraction
from collections import Counter

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]


def playerMaptoMongo(player):
    # dump to JSON string

    playerJSONString = json.dumps(player, default=lambda o: serializePlayerAttribute(o))

    playerDict = json.loads(playerJSONString)

    # remove some keys we won't need

    [playerDict.pop(k) for k in ['active', 'sub', 'position', 'battingGameStats', 'pitchingGameStats']]

    # move probabilities out of ratings so it makes sense

    playerDict['probabilities'] = {}

    playerDict['probabilities']['batting'] = playerDict['ratings'].pop('batting')
    playerDict['probabilities']['pitching'] = playerDict['ratings'].pop('pitching')

    # rearrange stats for extensibility

    playerDict['stats'] = {}
    playerDict['stats'][CURRENT_SEASON] = {}

    playerDict['stats'][CURRENT_SEASON]['batting'] = playerDict.pop('battingCareerStats')
    playerDict['stats'][CURRENT_SEASON]['pitching'] = playerDict.pop('pitchingCareerStats')

    # add back in IP

    # playerDict['stats'][CURRENT_SEASON]['pitching']['IP'] = {}
    # playerDict['stats'][CURRENT_SEASON]['pitching']['IP']['numerator'] = ipNum
    # playerDict['stats'][CURRENT_SEASON]['pitching']['IP']['denominator'] = ipDenom

    # adding a field for twitter avatar URL (will implement later)

    playerDict['avatarURL'] = ""

    # add a field for a pitcher's last start 

    # playerDict['lastStart'] = datetime.utcnow()

    return playerDict


def serializePlayerAttribute(attribute):
    if isinstance(attribute, Fraction):
        return {"numerator": attribute.numerator, "denominator": attribute.denominator}

    else:
        return attribute.__dict__


def mongoMapToPlayer(mongoPlayer, blankPlayer):
    tbPlayer = blankPlayer

    for key in ['id', 'name', 'fullName', 'handle', 'handedness', 'uniNumber']:
        setattr(tbPlayer, key, mongoPlayer[key])

    tbPlayer.battingCareerStats = Counter(mongoPlayer['stats'][CURRENT_SEASON]['batting'])

    mongoPitchingStats = mongoPlayer['stats'][CURRENT_SEASON]['pitching']

    oldIP = mongoPitchingStats.pop('IP')
    newIP = Fraction(oldIP['numerator'], oldIP['denominator'])
    mongoPitchingStats['IP'] = newIP

    tbPlayer.pitchingCareerStats = Counter(mongoPitchingStats)

    for key in ['contact', 'power', 'discipline', 'control', 'stuff', 'composure']:
        setattr(tbPlayer.ratings, key, mongoPlayer['ratings'][key])

    tbPlayer.ratings.batting = mongoPlayer['probabilities']['batting']
    tbPlayer.ratings.pitching = mongoPlayer['probabilities']['pitching']

    return tbPlayer


def mongoPlayerSave(mongoPlayer):
    db.players.find_one_and_update({'id': mongoPlayer['id']}, {'$set': mongoPlayer}, upsert=True)


def mongoDeleteByTwitterId(id):
    db.players.delete_one({'id': id})


def mongoReturnAll():
    return list(db.players.find())


def mongoGetAllTwitterIds():
    return [a['id'] for a in list(db.players.find({}, {'id': 1}))]


def mongoGetPlayersByLastStartAscending(count):
    return list(db.players.find().sort('lastStart', pymongo.ASCENDING).limit(count))
