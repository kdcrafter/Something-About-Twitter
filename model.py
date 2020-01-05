import tensorflow as tf
import numpy as np
import pickle
import os
import mysql.connector
import config

#disable AVX2 warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

def build_model(tokens_size, embedding_dim, rnn_units, batch_size): #TODO: add mask variable
    model = tf.keras.Sequential([
        tf.keras.layers.Masking(),
        tf.keras.layers.Embedding(tokens_size, embedding_dim, 
                                batch_input_shape=[batch_size, None]),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSMT(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSMT(rnn_units,
                        return_sequences=True,
                        stateful=True,
                        recurrent_initializer='glorot_uniform'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(tokens_size)
    ])
    return model

def main():
    #vectorize TODO: make comment sections into functions
    with open('tokens.pkl', 'rb') as file:
        tokens = pickle.load(file)

    str2index = {str:index for index, str in enumerate(tokens)}
    index2str = np.array(list(tokens))

    #get data
    db = mysql.connector.connect(
        host='localhost',
        user=config.USERNAME,
        passwd=config.PASSWORD,
        database=config.DATABASE_NAME
    )
    cursor = db.cursor()

    cursor.execute('SELECT text FROM tweets')
    tweets = cursor.fetchall()

    #create padded dataset of character len(tokens) where that character is a mask
    dataset = np.full((len(tweets), config.MAX_TWEET_LENGTH), len(tokens))

    for index, tweet in enumerate(tweets):
        tweet = np.array([str2index[char] for char in tweet[0]]) #tweet[0] because tweet is a tuple
        dataset[index][:tweet.size] = tweet
            
    #prepare dataset
    dataset_divide = int(dataset.shape[0]*config.TRAIN_VAL_SPLIT)
    train_dataset = tf.data.Dataset.from_tensor_slices(dataset[:dataset_divide])
    val_dataset = tf.data.Dataset.from_tensor_slices(dataset[dataset_divide:])

    train_dataset = train_dataset.map(split_input_target).shuffle(config.BUFFER_SIZE)
    val_dataset = val_dataset.map(split_input_target).shuffle(config.BUFFER_SIZE)

    train_dataset = train_dataset.batch(config.BATCH_SIZE, drop_remainder=True)
    val_dataset = val_dataset.batch(config.BATCH_SIZE, drop_remainder=True)

    #create model

    #train model
    
    checkpoint_callback=tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_prefix,save_weights_only=True)

    history = model.fit(train_dataset, epochs=config.EPOCHS, callbacks=[checkpoint_callback, early_stop] , validation_data=val_dataset)

    with open('history.pkl', 'wb') as file:
        pickle.dump(history, file)

if __name__ == '__main__':
    main()


