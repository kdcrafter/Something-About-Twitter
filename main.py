from config import *
import tweepy as tw

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

search_words = "the"

tweets = tw.Cursor(api.search, q=search_words, lang="en").items(5)

for tweet in tweets:
    print(tweet.text)