import re
import collections
import string
import config
import mysql.connector
import pickle

#Note: to see the current iteration, please run the file with -u (to skip buffering)

def get_vocab():
    vocab = collections.defaultdict(int)

    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD,
        database=config.DATABASE_NAME
    )
    cursor = db.cursor()

    cursor.execute('SELECT text FROM tweets')
    tweets = cursor.fetchall()

    for tweet in tweets:
        words = tweet[0].strip().split()
        for word in words:
            vocab[' '.join(word)] += 1 #stored as a spaced string to make replacing text easier

    return vocab

def get_pairs(vocab):
    pairs = collections.defaultdict(int)

    for word, freq in vocab.items():
        tokens = word.split()
        for token, next_token in list(zip(tokens, tokens[1:])):
            pairs[token,next_token] += freq

    return pairs

def merge_vocab(pair, vocab):
    new_vocab = collections.defaultdict(int)

    for word in vocab:
        #combine each instance of pair to form one token
        new_word = re.sub(re.escape(' '.join(pair)), ''.join(pair), word)
        new_vocab[new_word] = vocab[word]

    return new_vocab

def main():
    print('begin byte encoding')

    vocab = get_vocab()
    tokens = set(string.printable)

    print('iteration: ', end='')
    for i in range(config.MAX_NEW_TOKENS):
        print(i, end=', ')

        pairs = get_pairs(vocab)
        if not pairs:
            print('no new tokens to add')
            break

        most_frequent_pair = max(pairs, key=pairs.get)
        vocab = merge_vocab(most_frequent_pair, vocab)
        tokens.add(''.join(most_frequent_pair))
    print() #newline

    print('tokens:', tokens)
    print('byte encoding complete')

    with open('tokens.pkl', 'wb') as file:
        pickle.dump(tokens, file)

if __name__ == '__main__':
    main()