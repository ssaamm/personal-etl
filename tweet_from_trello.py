import json

import tweepy
import trello

from utils.secrets import TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN_KEY, TW_ACCESS_TOKEN_SECRET, TRELLO_APP_KEY, TRELLO_TOKEN

def get_cards(list_id='59e7eade486873e09eb165d9'):
    lists = trello.Lists(TRELLO_APP_KEY, TRELLO_TOKEN)
    cards = lists.get_card(list_id)
    return [c['name'] for c in cards]

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(TW_CONSUMER_KEY, TW_CONSUMER_SECRET)
    auth.set_access_token(TW_ACCESS_TOKEN_KEY, TW_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    to_tweet = get_cards()
    if any(len(t) > 140 for t in to_tweet):
        print "WARNING: Can't tweet:", t, '(too long)'

    status = next((t for t in to_tweet if len(t) < 140), None)
    print 'Tweeting:', status

    api.update_status(status)
