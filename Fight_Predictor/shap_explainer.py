import matplotlib.pyplot as plt
import shap
import tensorflow as tf
import numpy as np
import os
from tensorflow import keras

from preprocess_data import FightDataPreprocessor
from utils import get_train_test_data, r2
from sklearn.externals import joblib

current_dir = os.path.join(os.getcwd(),'Fight_Predictor')
print('Current Dir is' + current_dir)

filepath = os.path.join(current_dir,'Saved_Models','Winner_Prediction_Models','bout_winner.h5')
model = keras.models.load_model(filepath)


fdp = FightDataPreprocessor()
fdp.data_pipeline_winner_prediction()
feature_names = fdp.feature_names
features = fdp.original_values

x_train, y_train, x_test, y_test = get_train_test_data('winner_prediction_data')
scaler = joblib.load(os.path.join(os.getcwd(),'Fight_Predictor','my_scaler.pkl'))


explainer = shap.DeepExplainer(model,x_train)
shap_values = explainer.shap_values(x_test[:10])

feature_values = x_train[0].reshape(1,-1)
feature_values = scaler.inverse_transform(feature_values)

#shap.summary_plot(shap_values,feature_names=feature_names)
plot = shap.force_plot(
    explainer.expected_value[0],
    shap_values[0][0],feature_values,
    feature_names= feature_names, 
    )

print(y_train[0])
shap.save_html('explainer.html',plot)
shap.summary_plot(shap_values,features=x_train,feature_names= feature_names,plot_type= 'dot')



print('completed')
