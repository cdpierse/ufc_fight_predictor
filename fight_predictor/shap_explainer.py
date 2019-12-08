import matplotlib.pyplot as plt
import shap
import tensorflow as tf
import numpy as np
import os
from tensorflow import keras

from preprocess_data import FightDataPreprocessor
from utils import get_train_test_data, r2
from sklearn.externals import joblib

current_dir = os.path.join(os.getcwd(),'fight_predictor')
print('Current Dir is' + current_dir)

#filepath = os.path.join(current_dir,'Saved_Models','Winner_Prediction_Models','bout_winner.h5')
filepath = os.path.join(current_dir,'Saved_Models','Fight_Stats_Models','fighter_stats.h5')

#model = keras.models.load_model(filepath)
model = keras.models.load_model(filepath,custom_objects={'r2': r2})



with open('fight_stats_feature_names.txt','r',encoding='utf-8') as f:
    contents = f.readlines()

feature_names = [x.strip()for x in contents]

#x_train, y_train, x_test, y_test = get_train_test_data('winner_prediction_data')
x_train, y_train, x_test, y_test = get_train_test_data('fighter_stats_prediction_data')

scaler = joblib.load(os.path.join(os.getcwd(),'fight_predictor','my_scaler.pkl'))

upper_index = 100
explainer = shap.DeepExplainer(model,x_train)
shap_values = explainer.shap_values(x_train[:upper_index])

feature_values = x_train[:upper_index]
feature_values = scaler.inverse_transform(feature_values)

#shap.summary_plot(shap_values,feature_names=feature_names)
# plot = shap.force_plot(
#     explainer.expected_value[0],
#     shap_values[0][:],feature_values,
#     feature_names= feature_names, 
#     )

print(y_train[0])
#shap.save_html('explainer.html',plot)

shap.summary_plot(shap_values[0],features = feature_values,feature_names= feature_names)


print('completed')
