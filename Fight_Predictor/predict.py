import os
import pandas as pd
from processor import ProductionProcessor, ProductionStatsProcessor
from utils import r2
from tensorflow import keras
import sys
import numpy as np


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
            'Fight_Predictor', 'Data', 'Scraped_Data', 'scraped_fighters.csv')
        try:
            self.fighters = pd.read_csv(filedir)
        except:
            sys.exit('Unable to read Fighters file from disk. Exiting.')

    def set_feature_names(self):
        base_dir = os.path.join('Fight_Predictor', 'Data',
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
        psp = ProductionStatsProcessor(
            fight_bouts=self.stats_prediction_df, columns=self.stats_feature_names)
        psp.main()
        self.stats_prediction_df = psp.fight_bouts


class Predict:

    def __init__(self, fighter_pairs, stats_model, winner_model=None):
        self.stats_model = stats_model
        self.fighter_pairs = fighter_pairs
        self.reversed_pairs = []

    def predict_stats(self, array):
        return self.stats_model.predict(array)

    def reverse_fight_pairs(self):
        for pair in self.fighter_pairs:
            self.reversed_pairs.append((pair[1], pair[0]))

    # predicts stats for both orderings of the df
    def get_average_predictions(self):

        arr1 = PreparePredictions().create_stats_df(self.fighter_pairs)
        arr2 = PreparePredictions().create_stats_df(self.reversed_pairs)
        preds1 = self.predict_stats(arr1)
        preds2 = self.predict_stats(arr2)
        print(PreparePredictions().stats_target_names)
        print(np.max(np.array([preds1, preds2]), axis=0)[0])


if __name__ == "__main__":
    base_dir = os.path.join(os.getcwd(), 'Fight_Predictor', 'Files', 'Models')
    stats_model = keras.models.load_model(os.path.join(
        base_dir, 'stats_model.h5'), custom_objects={'r2': r2})
    # p = PreparePredictions(stats_model)
    fight_pair = [('Conor McGregor', 'Nate Diaz'),
                  ('Daniel Cormier', 'Jon Jones')]
    # p.create_stats_df(fight_pair)
    p = Predict(fight_pair, stats_model)
    p.reverse_fight_pairs()
    p.get_average_predictions()
