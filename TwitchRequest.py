import os
import requests
import time
import json
from TwitterBot import postTweet
import pymongo
from datetime import datetime

'''
How to get a new bearer token? Look up Twitch Dev Console and "Twitch OAuth token".
Use Postman and send a POST request for a new OAuth token. This is of type "Bearer".
'''

CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
BEARER_TOKEN = os.environ['TWITCH_BEARER_TOKEN']
MONGODB_AUTH = os.environ['MONGODB_AUTH']

#CHANNEL_NAME = 'https://api.twitch.tv/helix/streams?user_id=51496027' # ex:loltyler1
#CHANNEL_NAME = 'https://api.twitch.tv/helix/streams?user_login=Gosu'
CHANNEL_NAME = 'https://api.twitch.tv/helix/streams'

INTERVAL = 60 * 3  # check stream status every 3 minutes.

# connect to database
cluster = pymongo.MongoClient(MONGODB_AUTH)
db = cluster.test
collection = db['LiveStatus']

headChannel = {
    'client-id' : CLIENT_ID, 
    "Authorization": BEARER_TOKEN
}
payloadChannel = { 
    #'user-id' : '51496027', # can use a streamer's ID
    'user_login' : 'xQcOw' # can use a streamer's display name
}

def checkOnStream():
    # API call
    r = requests.get(url = CHANNEL_NAME, headers = headChannel, params = payloadChannel)
    # data output
    rDict = json.loads(r.text)
    #print(rDict)
    # is the stream currently on
    online = False
    if len(rDict['data']) != 0:
        online = True
    #print("Parsed LiveStatus:", online)
    # Check if stream went offline
    if not online:
        doc = collection.find_one({'channelName' : 'xQcOw'})
        liveStatus = doc['liveStatus'] # 0=offline, 1=online
        if liveStatus == 1:
            collection.update_one({'channelName': 'xQcOw'}, {'$set': {'liveStatus': 0}})
            collection.update_one({'channelName': 'xQcOw'}, {'$set': {'category': ''}})
            postTweet(message='xQc is now offline. I hope you enjoyed your stay!', streamEnd=True)
            print('Posted tweet: xQc is now offline.')
    else:
        streamInfo = rDict['data'][0]
        streamTitle = streamInfo['title']
        gameID = streamInfo['game_id']
        #print("TITLE:", streamTitle)
        #print("GAME ID:", gameID)
        # check if stream just went live
        doc = collection.find_one({'channelName' : 'xQcOw'})
        liveStatus = doc['liveStatus'] # 0=offline, 1=online
        if liveStatus == 0:
            #now = datetime.now()
            #dateTimeStr = now.strftime("%m/%d/%Y/%H/%M") # month, day, year, hour, minute
            collection.update_one({'channelName': 'xQcOw'}, {'$set': {'liveStatus': 1}})
            postTweet(message='xQc is live! {}'.format(streamTitle), streamStart=True) 
            print('Posted tweet: xQc is live!')
            return
        # stream has been live, now check the category
        GAME_TITLE = 'https://api.twitch.tv/helix/games'
        headGame = {
            'client-id' : CLIENT_ID, 
            "Authorization": BEARER_TOKEN
        }
        payloadGame = {
            'id' : gameID
        }
        g = requests.get(url = GAME_TITLE, headers = headGame, params = payloadGame)
        #print(g.text)
        gDict = json.loads(g.text)
        gameInfo = gDict['data'][0]
        gameName = gameInfo['name']
        #print("GAME:", gameName)
        # did the game category change?
        prevCategory = doc['category']
        if prevCategory != gameName:
            collection.update_one({'channelName': 'xQcOw'}, {'$set': {'category': gameName}})
            postTweet(message='xQc is now playing {}!'.format(gameName), gameName=gameName)
            print('Posted tweet: xQc is now streaming a different category!')
    #print('Finished checking stream status.')

while True:
    now = datetime.now()
    dateTimeStr = now.strftime("%m/%d/%Y/%H/%M") # month, day, year, hour, minute
    print(f"Checking xQcOw's stream status at {dateTimeStr}")
    checkOnStream()
    time.sleep(INTERVAL)
