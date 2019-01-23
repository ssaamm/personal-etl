import json

import tweepy
import trello

from utils.secrets import TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN_KEY, TW_ACCESS_TOKEN_SECRET, TRELLO_APP_KEY, TRELLO_TOKEN

def get_cards(list_id='59e7eade486873e09eb165d9'):
    lists = trello.Lists(TRELLO_APP_KEY, TRELLO_TOKEN)
    return lists.get_card(list_id)

def archive_card(card):
    cards = trello.Cards(TRELLO_APP_KEY, TRELLO_TOKEN)
    cards.update_closed(card['id'], 'true')

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(TW_CONSUMER_KEY, TW_CONSUMER_SECRET)
    auth.set_access_token(TW_ACCESS_TOKEN_KEY, TW_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    to_tweet = get_cards()
    card = next((c for c in to_tweet if len(c['name']) < 280), None)
    if card is None:
        print 'no tweets'
        exit(1)
    status = card['name']

    api.update_status(status)
    archive_card(card)
