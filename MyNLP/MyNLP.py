import tweepy
from tweepy import OAuthHandler
import api_config

auth = OAuthHandler(api_config.consumer_key, api_config.consumer_secret)
auth.set_access_token(api_config.access_token, api_config.access_secret)

api = tweepy.API(auth)

for status in tweepy.Cursor(api.home_timeline).items(10):
    # Process a single status
    print(status.text)
