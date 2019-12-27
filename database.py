import mysql.connector
import config
import time
import tweepy as tw

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

def drop_database(DATABASE_NAME):
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD
    )

    cursor = db.cursor()
    cursor.execute(f'DROP DATABASE {config.DATABASE_NAME}')
    print('database dropped')

def init_database():
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD,
        database=config.DATABASE_NAME
    )

    cursor = db.cursor()
    cursor.execute("""CREATE TABLE tweets (
        id INT PRIMARY KEY,
        tweet varchar(255)
    )""")

    print('database initialized')
