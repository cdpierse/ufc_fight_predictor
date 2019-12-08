import os
import sys

import numpy as np
import pandas as pd
from tensorflow import keras

from processor import ProductionProcessor
from utils import r2


class PreparePredictions:  
            
    def __init__(self):
        # the above params are not yet coded.
        self.get_fighters()
        self.set_feature_names()
        self.stats_prediction_df = pd.DataFrame(
            columns=self.stats_feature_names)

    def get_fighters(self):
        " Loads the scraped_fighters csv file into a dataframe "
        filedir = os.path.join(
            'fightPredictor', 'Data', 'Scraped_Data', 'scraped_fighters.csv')
        try:
            self.fighters = pd.read_csv(filedir)
        except Exception:
            sys.exit('Unable to read Fighters file from disk. Exiting.')

    def set_feature_names(self):
        base_dir = os.path.join('fightPredictor', 'Data',
                                'Processed_Data')
        stats_dir = os.path.join(base_dir, 'Fight_Stats', 'data.npz')
        winner_dir = os.path.join(base_dir, 'Fight_Winner', 'data.npz')
        self.winner_feature_names = np.load(winner_dir)['feature_names']
        self.stats_feature_names = list(np.load(stats_dir)['feature_names'])
        self.stats_target_names = np.load(stats_dir)['fight_stats_columns']
        self.x_train = np.load(stats_dir)['x_train']

    def get_fighter_data(self, fighter_name):
        " Returns matched fighter career stats for a given fighter name from scraped_fighters.csv"
        return self.fighters[self.fighters.fighter_name == fighter_name]

    def get_fighter_pair_stats(self, pair):
        self.f1_stats = self.get_fighter_data(pair[0])
        self.f2_stats = self.get_fighter_data(pair[1])

    def create_stats_df(self, fighter_pairs):
        "Takes a list of fighter name tuples and builds up a dataframe where each row represents a bout to predicted"
        if isinstance(fighter_pairs, list):
            for pair in fighter_pairs:
                # dynamically resets f1 and f2 stats for each pair
                self.get_fighter_pair_stats(pair)
                prefixes = ['f1', 'f2']
                columns = list(self.stats_prediction_df.columns)
                temp_df = pd.DataFrame(
                    columns=columns)

                for prefix in prefixes:
                    # explicit mapping of features from self.fighters to their fight_bout counterparts
                    stats_df_mapping = {
                        'date_of_birth': prefix + '_dob',
                        'fighter_record': prefix + '_record',
                        'height': prefix + '_height',
                        'reach': prefix + '_reach',
                        'sapm': prefix + '_sapm',
                        'slpm': prefix + '_slpm',
                        'stance': prefix + '_stance',
                        'strike_acc': prefix + '_stk_acc',
                        'strike_def': prefix + '_stk_def',
                        'sub_avg': prefix + '_sub_avg',
                        'td_acc': prefix + '_td_acc',
                        'td_avg': prefix + '_td_avg',
                        'td_def': prefix + '_td_def',
                        'weight': prefix + '_weight'
                    }

                    for k, v in stats_df_mapping.items():
                        if prefix == 'f1':
                            temp_df[v] = self.f1_stats[k].values
                        else:
                            temp_df[v] = self.f2_stats[k].values
                self.stats_prediction_df = self.stats_prediction_df.append(
                    temp_df, ignore_index=True, sort=False)

        else:
            print('fighter_pairs is not of type <list>')

        self.process_stats_df()

        return self.stats_prediction_df

    def process_stats_df(self):
        pp = ProductionProcessor(
            fight_bouts=self.stats_prediction_df, columns=self.stats_feature_names)
        pp.stats_main()
        self.unscaled_stats_df = pp.unscaled_df
        self.stats_prediction_df = pp.fight_bouts

    def create_winner_df(self, predictions):
        predicted_stats = pd.DataFrame(
            data=predictions, columns=self.stats_target_names)
        self.winner_df = pd.concat(
            [predicted_stats, self.unscaled_stats_df], axis=1)

    def process_winner_df(self):
        pp = ProductionProcessor(
            fight_bouts=self.winner_df, columns=self.winner_feature_names)
        pp.winner_main()
        self.winner_df = pp.fight_bouts


class Predict:

    def __init__(self, fighter_pairs, stats_model, winner_model):
        self.stats_model = stats_model
        self.winner_model = winner_model
        self.fighter_pairs = fighter_pairs
        self.reversed_pairs = []
        self.reverse_fight_pairs()
        self.get_average_predictions()

    def predict_stats(self, array):
        return self.stats_model.predict(array)

    def predict_winner(self, array):
        return self.winner_model.predict(array)

    def reverse_fight_pairs(self):
        for pair in self.fighter_pairs:
            self.reversed_pairs.append((pair[1], pair[0]))

    # predicts stats for both orderings of the df
    def get_average_predictions(self):

        winner_preds = self.get_predictions(self.fighter_pairs)
        reversed_winner_preds = self.get_predictions(self.reversed_pairs)

        winner_preds = self.create_abs_probability_array(winner_preds)
        reversed_winner_preds = self.create_abs_probability_array(
            reversed_winner_preds)

        final_winners_predicted = []
        for i, (pair1, pair2) in enumerate(zip(self.fighter_pairs, self.reversed_pairs)):
            # if it selects the same fighter each time that fighter is the predicted winner
            if winner_preds[i][0] is 'fighter1' and reversed_winner_preds[i][0] is 'fighter2':
                avg_prob = np.mean(
                    [winner_preds[i][1], reversed_winner_preds[i][1]])
                final_winners_predicted.append((pair1[0], avg_prob))
            else:  # two different winners have been selected, return winner w/ highest prob
                if winner_preds[i][1] > reversed_winner_preds[i][1]:
                    final_winners_predicted.append(
                        (pair1[0], winner_preds[i][1]))
                elif winner_preds[i][1] < reversed_winner_preds[i][1]:
                    final_winners_predicted.append(
                        (pair2[0], reversed_winner_preds[i][1]))
                elif winner_preds[i][1] == reversed_winner_preds[i][1]:
                    final_winners_predicted.append(
                        ((pair1[0], pair2[0]), 'Draw'))
        self.predictions = final_winners_predicted

    def get_predictions(self, fighter_pairs):
        pp = PreparePredictions()
        stats_data = pp.create_stats_df(fighter_pairs)
        stats_predictions = self.predict_stats(stats_data)
        pp.create_winner_df(stats_predictions)
        pp.process_winner_df()
        winner_predictions = self.predict_winner(pp.winner_df)
        return winner_predictions

    def create_abs_probability_array(self, predictions):
        abs_probs = []
        for prediction in list(predictions):
            if prediction < 0.50:
                abs_pred = ('fighter1', abs(prediction[0] - 0.5) / 0.5)
            else:
                abs_pred = ('fighter2', abs(prediction[0] - 0.5) / 0.5)

            abs_probs.append(abs_pred)

        return abs_probs


if __name__ == "__main__":
    base_dir = os.path.join(os.getcwd(), 'fightPredictor', 'Files', 'Models')
    stats_model = keras.models.load_model(os.path.join(
        base_dir, 'stats_model.h5'), custom_objects={'r2': r2})
    winner_model = keras.models.load_model(os.path.join(
        base_dir, 'winner_model.h5'))

    fight_pair = [('Nick Diaz', 'Nate Diaz'),
                  ('Stipe Miocic', 'Daniel Cormier')]
    p = Predict(fight_pair, stats_model, winner_model)
    print(p.predictions)
