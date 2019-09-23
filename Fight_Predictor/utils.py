import tensorflow.keras.backend as K
import numpy as np
import os

def r2(y_true, y_pred):
    SS_res = K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true)))
    return 1 - SS_res/(SS_tot + K.epsilon())


def random_data_shuffle(x_train,y_train):
    s = np.arange(x_train.shape[0])
    np.random.shuffle(s)
    x_train = x_train[s]
    y_train = y_train[s]

    return x_train,y_train


def get_train_test_data(folder_name):
    directory = os.path.join('Fight_Predictor', 'Data',
                             'Processed_Data', folder_name)
    with np.load(os.path.join(directory, 'data.npz')) as data:
        x_train = data['x_train']
        y_train = data['y_train']
        x_test = data['x_test']
        y_test = data['y_test']

    return x_train, y_train, x_test, y_test
