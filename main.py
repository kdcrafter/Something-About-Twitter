import config
import tweepy as tw

def main():
    auth = tw.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    api = tw.API(auth)

    tweets = api.search(q='gaming', lang='en')[0]

    print(tweets)

    # tweets = tw.Cursor(api.search, q='#', lang='en').items(1)

    # for tweet in tweets:
    #     print(tweet.text)
    #     print('-----------------------')

if __name__ == '__main__':
    main()