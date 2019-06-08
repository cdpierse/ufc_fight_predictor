import tensorflow as tf
import numpy as np
np.random.seed(7)

x_train = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/X_train.csv', delimiter=',')
y_train = np.genfromtxt('Fight_Predictor/model_data/winner_prediction_data/y_train.csv', delimiter=',')
x_test = np.genfromtxt('Fight_Predictor/model_data/X_test.csv', delimiter=',')
y_test = np.genfromtxt('Fight_Predictor/model_data/y_test.csv', delimiter=',')


hidden_units1 = 120 #150
hidden_units2 = 120 #150 for both h1 and h2 works well
epochs = 450 #was 450
l2_reg = tf.keras.regularizers.l2(0.001)
# #
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(hidden_units1,
                                input_dim=x_train.shape[1],
                                activation='relu',

                                kernel_initializer='normal',
                                activity_regularizer=l2_reg))
model.add(tf.keras.layers.Dropout(0.6))
model.add(tf.keras.layers.BatchNormalization())
model.add(tf.keras.layers.Dense(hidden_units2,
                                activation='relu',
                                kernel_initializer='normal',
                                activity_regularizer=l2_reg))
model.add(tf.keras.layers.Dropout(0.6))
model.add(tf.keras.layers.BatchNormalization())
model.add(tf.keras.layers.Dense(1,activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer= tf.keras.optimizers.Adam(0.0001),metrics=['accuracy'])

model.fit(x_train,y_train, epochs= epochs, batch_size= 64,validation_split= 0.05)

scores = model.evaluate(x_test,y_test)

print(model.summary())


