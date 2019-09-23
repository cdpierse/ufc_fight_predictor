import os
import sys

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout

from utils import get_train_test_data, random_data_shuffle

np.random.seed(7)


def winner_model():

    x_train, y_train, x_test, y_test = get_train_test_data(
        'Fight_Winner')

    x_train, y_train = random_data_shuffle(x_train, y_train)

    hidden_units = 300  # 150
    epochs = 170
    DROPOUT = 0.65
    l2_reg = tf.keras.regularizers.l2(0.001)

    model = tf.keras.models.Sequential()
    model.add(Dense(hidden_units, input_dim=x_train.shape[1], activation='relu',
                    kernel_initializer='normal', activity_regularizer=l2_reg, name='layer1'))

    model.add(Dropout(DROPOUT))

    model.add(Dense(hidden_units, activation='relu',
                    kernel_initializer='normal', activity_regularizer=l2_reg, name='layer2'))

    model.add(Dropout(DROPOUT))

    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=tf.keras.optimizers.Adam(
        0.0001), metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=epochs,
              batch_size=128, validation_split=0.05)

    scores = model.evaluate(x_test, y_test)

    print(model.summary())


def fight_stats_model():
    pass


winner_model()
