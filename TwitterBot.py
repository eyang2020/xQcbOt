import os
import random
import tweepy

API_KEY = os.environ['TWITTER_API_KEY']
API_SECRET = os.environ['TWITTER_API_SECRET']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True)

# init list of gifs used for stream start
gifList = [
    'xqc01.gif',
    'xqc02.gif',
    'xqc03.gif',
    'xqc04.gif',
    'xqc05.gif',
    'xqc06.gif',
    'xqc07.gif',
    'xqc08.gif',
    'xqc09.gif',
    'xqc10.gif',
]

# Verify Credentials
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# Create a tweet
def postTweet(message, gameName='', streamStart=False, streamEnd=False):
    try:
        # first handle streamStart and streamEnd
        if streamStart:
            # pick a random gif from gifList
            gifName = random.choice(gifList)
            media = api.media_upload('xqc-gifs/{}'.format(gifName))
            # append 'LIVE' to name
            api.update_profile(name='xQcbOt (LIVE 🔴)')
            api.update_status(status=message, media_ids=[media.media_id])
        elif streamEnd:
            media = api.media_upload('xqcoutro.gif')
            api.update_status(status=message, media_ids=[media.media_id])
            # set username back to normal
            api.update_profile(name='xQcbOt')
        else:
            # below, we can add any specific tweet changes for a specific game category
            # a tweet here means the stream is ongoing and the category has changed
            if gameName == 'Grand Theft Auto V':
                gameName = 'NoPixel RP'
                message = 'xQc is now playing NoPixel RP!'
            api.update_status(message)
    except tweepy.TweepError as error:
        if error.api_code == 187: # duplicate status error
            api.update_status(f'xQc is now streaming {gameName}!') # this should be most recent category # just change the structure of tweet
        else:
            print('Status was recently posted.')
            raise error
