import mysql.connector
import config
import time
import tweepy as tw
import string

def create_database():
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD
    )

    cursor = db.cursor()

    cursor.execute('SHOW DATABASES')
    if (config.DATABASE_NAME,) in cursor:
        print('database exists')
    else:
        cursor.execute(f'CREATE DATABASE {config.DATABASE_NAME}')
        print('database created')

    db.close()

def drop_database(DATABASE_NAME):
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD
    )

    cursor = db.cursor()
    cursor.execute(f'DROP DATABASE {config.DATABASE_NAME}')
    print('database dropped')

    db.close()

def init_database():
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD,
        database=config.DATABASE_NAME
    )

    cursor = db.cursor()
    cursor.execute(f"""CREATE TABLE tweets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        text varchar({config.MAX_TWEET_LENGTH})
    )""")
    cursor.execute(f"""CREATE TABLE replies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        text varchar({config.MAX_TWEET_LENGTH})
    )""")

    print('database initialized')

    db.close()

class Listener(tw.StreamListener):
    def __init__(self, time_limit): #in seconds
        super().__init__()
        self.start_time = time.time()
        self.time_limit = time_limit

        self.db = mysql.connector.connect(
            host='localhost',
            user=config.USERNAME,
            passwd=config.PASSWORD,
            database=config.DATABASE_NAME
        )
        self.cursor = self.db.cursor()
    
    def on_status(self, tweet):
        if (time.time() - self.start_time) > self.time_limit: #stop when needed
            self.db.commit()
            self.db.close()
            return False
        
        if tweet.retweeted or 'RT @' in tweet.text: #no retweets
            return True

        #get and edit text
        if tweet.truncated:
            text = tweet.extended_tweet['full_text']
        else:
            text = tweet.text
        text = ''.join(filter(lambda char : char in string.printable, text))

        if len(text) > config.MAX_TWEET_LENGTH: #no long tweets
            return True

        #add row to database
        if tweet.in_reply_to_status_id == None:
            sql = "INSERT INTO tweets (text) VALUES (%s)"
        else:
            sql = "INSERT INTO replies (text) VALUES (%s)"

        val = (text,)
        self.cursor.execute(sql, val)

        return True

    def on_error(self, status):
        print(status)

def get_data():
    print('receiving data')

    auth = tw.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

    stream = tw.Stream(auth, Listener(time_limit=config.GET_DATA_TIME_LIMIT), lang='en', tweet_mode='extended')
    stream.filter(track=['a', 'the', 'i', 'you', 'u'], languages=['en'])

    print('received data')

def main():
    create_database()
    init_database()
    get_data()

if __name__ == '__main__':
    main()
