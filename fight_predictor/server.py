import os

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from tensorflow import keras

from predict import Predict
from utils import r2

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.join(os.getcwd(),'Files', 'Models')


@app.route("/api/v1.0/predict", methods=['GET']) 
def get_prediction():
    print(BASE_DIR)
    stats_model = keras.models.load_model(os.path.join(
        BASE_DIR, 'stats_model.h5'), custom_objects={'r2': r2})
    winner_model = keras.models.load_model(os.path.join(
        BASE_DIR, 'winner_model.h5'))
    fighter1 = request.args.get('fighter1')
    fighter2 = request.args.get('fighter2')
    prediction_tuple = [(fighter1, fighter2)]
    print('I also get here')
    p = Predict(prediction_tuple, stats_model, winner_model)
    print('I get passed here')
    raw_response = p.predictions[0]
    response = {"winner":str(raw_response[0]),"confidence":str(float(raw_response[1]))}
    #response = f'{str(raw_response[0]), str(float(raw_response[1]))}'

    return jsonify(response)


@app.route("/api/v1.0/fighters", methods=['GET'])
def get_fighters():
    filedir = os.path.join(os.getcwd(),
        'Data',
        'Scraped_Data', 'scraped_fighters.csv')
    fighters = pd.read_csv(filedir)
    fighter_names = list(fighters.fighter_name.unique())
    return jsonify({'fighter_names': fighter_names})

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

    # code to fetch fighter list

if __name__ == "__main__":
    app.run(threaded=True, port=5000)
    # app.run(debug=True, host='0.0.0.0', port=5000)
