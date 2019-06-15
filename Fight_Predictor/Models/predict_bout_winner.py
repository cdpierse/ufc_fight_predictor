#rename this file to predict_bout_winner
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout

print(f'using tensorflow version {tf.__version__}')

np.random.seed(7)

x_train = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/X_train.csv', delimiter=',')
y_train = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/y_train.csv', delimiter=',')
x_test = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/X_test.csv', delimiter=',')
y_test = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/y_test.csv', delimiter=',')


s = np.arange(x_train.shape[0])
np.random.shuffle(s)
x_train = x_train[s]
y_train = y_train[s]

hidden_units = 300 #150
epochs = 300  

DROPOUT = 0.8

l2_reg = tf.keras.regularizers.l2(0.001)
# #
model = tf.keras.models.Sequential()
model.add(Dense(
                hidden_units,
                input_dim=x_train.shape[1],
                activation='relu',
                kernel_initializer='normal',
                activity_regularizer=l2_reg,
                name='layer1'
                )
        )

model.add(Dropout(DROPOUT))

model.add(Dense(
                hidden_units,
                activation='relu',
                kernel_initializer='normal',
                activity_regularizer=l2_reg,
                name='layer2'
                ),
        )

model.add(Dropout(DROPOUT))

model.add(Dense(1,activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer= tf.keras.optimizers.Adam(0.0001),metrics=['accuracy'])

model.fit(x_train,y_train, epochs= epochs, batch_size= 128,validation_split= 0.05)

scores = model.evaluate(x_test,y_test)

print(model.summary())
