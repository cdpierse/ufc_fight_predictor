import tensorflow as tf
import numpy as np
np.random.seed(7)

x_train = np.genfromtxt('model_data/X_train.csv', delimiter=',')
y_train = np.genfromtxt('model_data/y_train.csv', delimiter=',')
x_test = np.genfromtxt('model_data/X_test.csv', delimiter=',')
y_test = np.genfromtxt('model_data/y_test.csv', delimiter=',')

hidden_units1 = 120 #150
hidden_units2 = 120 #150 for both h1 and h2 works well
# #
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(150,input_dim=102,activation='relu',kernel_initializer='normal'))
model.add(tf.keras.layers.Dropout(0.6))
model.add(tf.keras.layers.BatchNormalization())
model.add(tf.keras.layers.Dense(150,activation='relu',kernel_initializer='normal'))
model.add(tf.keras.layers.Dropout(0.6))
model.add(tf.keras.layers.BatchNormalization())
model.add(tf.keras.layers.Dense(1,activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer= tf.keras.optimizers.RMSprop(0.0001),metrics=['accuracy'])

model.fit(x_train,y_train, epochs= 350, batch_size= 64,validation_split= 0.1)

scores = model.evaluate(x_test,y_test)


