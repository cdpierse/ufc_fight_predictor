import tensorflow as tf
import numpy as np
import tensorflow._api.v1.keras.backend as K
import datetime

x_train = np.genfromtxt('model_data/X_train_stats.csv', delimiter=',')
y_train = np.genfromtxt('model_data/y_train_stats.csv', delimiter=',')
x_test = np.genfromtxt('model_data/X_test_stats.csv', delimiter=',')
y_test = np.genfromtxt('model_data/y_test_stats.csv', delimiter=',')

def r2(y_true, y_pred):
    SS_res = K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true)))
    return 1 - SS_res/(SS_tot + K.epsilon())

epochs = 400

l2_reg = tf.keras.regularizers.l2(0.001)
" LAYER ONE "
model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(512,
                                input_dim=x_train.shape[1],
                                activation='linear',
                                kernel_initializer='normal',
                                activity_regularizer=l2_reg))
model.add(tf.keras.layers.Dropout(0.4))
model.add(tf.keras.layers.BatchNormalization())

" OUTPUT LAYER "
model.add(tf.keras.layers.Dense(y_train.shape[1],activation='linear'))

model.compile(loss='mse', optimizer= tf.keras.optimizers.Adam(0.0005),metrics=[r2])
history = model.fit(x_train,y_train, epochs= epochs, batch_size= 64, validation_split=0.05)

scores = model.evaluate(x_test,y_test)
results = model.predict(x_test)
time = str(datetime.datetime.now().date())
model.save('Saved_Models/Fight_Stats_Models/stats_model'+time+'.h5')

# predictor_cols = ['pass_stat_f1', 'pass_stat_f2', 'str_stat_f1', 'str_stat_f2',
#        'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 't d_stat_f2']
# for i in range(0,5):
#     rand_i = np.random.randint(0,300)
#     for prediction, actual, col in zip(results[rand_i], y_test[rand_i], predictor_cols):
#         print(f'{col}: Prediction= {prediction} Actual = {actual}')

