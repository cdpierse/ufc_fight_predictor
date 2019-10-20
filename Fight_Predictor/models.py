import sys
import os
import datetime
import sys

import numpy as np
import tensorflow as tf
import tensorflow._api.v1.keras.backend as K
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.regularizers import l2

from utils import r2, random_data_shuffle, get_train_test_data


np.random.seed(7)


def winner_model():
    """ Model for preidicting overall winner of a bout using static data and predicted bout stats"""

    x_train, y_train, x_test, y_test = get_train_test_data(
        'Fight_Winner')

    x_train, y_train = random_data_shuffle(x_train, y_train)

    hidden_units = 80  
    epochs = 170
    dropout = 0.65
    l2_reg = tf.keras.regularizers.l2(0.001)

    model = tf.keras.models.Sequential()
    model.add(Dense(hidden_units, input_dim=x_train.shape[1], activation='relu',
                    kernel_initializer='normal', kernel_regularizer=l2_reg, name='layer1'))

    model.add(Dropout(dropout))

    model.add(Dense(hidden_units, activation='relu',
                    kernel_initializer='normal', kernel_regularizer=l2_reg, name='layer2'))

    model.add(Dropout(dropout))

    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer=tf.keras.optimizers.Adam(0.0001),
                  metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=epochs,
              batch_size=32, validation_split=0.05)

    scores = model.evaluate(x_test, y_test)
    save(model, 'winner_model.h5')

    print(model.summary())


def fight_stats_model():

    x_train, y_train, x_test, y_test = get_train_test_data(
        'Fight_Stats')

    x_train, y_train = random_data_shuffle(x_train, y_train)

    epochs = 600
    hidden1 = 350
    dropout = 0.45
    l2_reg = l2(0.005)

    model = tf.keras.models.Sequential()
    model.add(Dense(hidden1, input_dim=x_train.shape[1], activation='relu',
                    kernel_initializer='normal', kernel_regularizer=l2_reg))
    model.add(Dropout(dropout))
    model.add(Dense(y_train.shape[1], activation='relu')) # relu here prevents negative output values 

    model.compile(
        loss='logcosh',
        optimizer=tf.keras.optimizers.Adam(0.0005),
        metrics=[r2]
    )

    history = model.fit(x_train, y_train,
                        epochs=epochs, batch_size=32,
                        validation_split=0.05,
                        shuffle=True
                        )

    scores = model.evaluate(x_test, y_test)
    save(model, 'stats_model.h5')

    results = model.predict(x_test)

    predictor_cols = [
        'pass_stat_f1', 'pass_stat_f2', 'str_stat_f1', 'str_stat_f2',
        'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 'td_stat_f2'
    ]

    for i in range(0, 20):
        rand_i = np.random.randint(0, 300)
        print('*' * 20)
        for prediction, actual, col in zip(results[rand_i], y_test[rand_i], predictor_cols):
            print(f'{col}: Prediction= {prediction} Actual = {actual}')


def save(model, save_name):
    save_loc = os.path.join(os.getcwd(), 'Fight_Predictor',
                            'Files', 'Models', save_name)
    model.save(save_loc)


winner_model()
fight_stats_model()
