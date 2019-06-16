import shap
import tensorflow as tf
from tensorflow import keras
from utils import r2,get_train_test_data
from preprocess_data import FightDataPreprocessor 
import matplotlib.pyplot as plt
filepath ='Fight_Predictor/Saved_Models/Winner_Prediction_Models/bout_winner.h5'
model = keras.models.load_model(filepath)


fdp = FightDataPreprocessor()
fdp.data_pipeline_winner_prediction()
feature_names = fdp.feature_names
x_train, y_train, x_test, y_test = get_train_test_data('winner_prediction_data')


explainer = shap.DeepExplainer(model,x_train)

shap_values = explainer.shap_values(x_test[:10])

#shap.summary_plot(shap_values,feature_names=feature_names)
plot = shap.force_plot(
    explainer.expected_value[1],
    shap_values[0][0],x_test[1],
    feature_names= feature_names,
    )
shap.save_html('explainer.html',plot)

print('completetd')