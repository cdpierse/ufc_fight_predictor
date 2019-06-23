#rename this file to predict_fighter_stats
import datetime
import sys

import numpy as np
import tensorflow as tf
import tensorflow._api.v1.keras.backend as K
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.regularizers import l2
from utils import r2,random_data_shuffle, get_train_test_data


x_train,y_train,x_test,y_test = get_train_test_data('fighter_stats_prediction_data')


x_train,y_train = random_data_shuffle(x_train,y_train)

epochs = 600
hidden1 = 350
DROPOUT = 0.45
l2_reg = l2(0.001)

model = tf.keras.models.Sequential()
model.add(Dense(
              hidden1,
              input_dim=x_train.shape[1],
              activation='relu',
              kernel_initializer='normal',
              activity_regularizer=l2_reg))
model.add(Dropout(DROPOUT))
model.add(Dense(y_train.shape[1]))

model.compile(
       loss='logcosh',
       optimizer= tf.keras.optimizers.Adam(0.0005),
       metrics=[r2]
       )

history = model.fit(
       x_train,
       y_train,
       epochs= epochs,
       batch_size= 128,
       validation_split= 0.05,
       shuffle= True
       )

model.save('Fight_Predictor/Saved_Models/Fight_Stats_Models/fighter_stats.h5')


scores = model.evaluate(x_test,y_test)
results = model.predict(x_test)


predictor_cols = ['pass_stat_f1', 'pass_stat_f2', 'str_stat_f1', 'str_stat_f2',
       'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 'td_stat_f2']
for i in range(0,20):
    rand_i = np.random.randint(0,300)
    print('*'*20)
    for prediction, actual, col in zip(results[rand_i], y_test[rand_i], predictor_cols):
        print(f'{col}: Prediction= {prediction} Actual = {actual}')
