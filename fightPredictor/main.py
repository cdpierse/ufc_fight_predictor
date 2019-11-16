import os

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from tensorflow import keras
from utils import r2
from predict import Predict

app = Flask(__name__)
CORS(app)


@app.route("/fight-predictor/api/v1.0/predict", methods=['POST'])
def main():
    print(os.getcwd())
    base_dir = os.path.join(os.getcwd(), 'fightPredictor', 'Files', 'Models')
    stats_model = keras.models.load_model(os.path.join(
        base_dir, 'stats_model.h5'), custom_objects={'r2': r2})
    winner_model = keras.models.load_model(os.path.join(
        base_dir, 'winner_model.h5'))
    print(request.json['data'])

    fight_pair = request.json['data']
    print(f'the fight_pair is {fight_pair}')
    fighter1, fighter2 = fight_pair['fighter1'], fight_pair['fighter2']
    prediction_tuple = [(fighter1, fighter2)]
    p = Predict(prediction_tuple, stats_model, winner_model)
    raw_response = p.predictions[0]
    response = f'{str(raw_response[0]), str(float(raw_response[1]))}'
    return response

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
