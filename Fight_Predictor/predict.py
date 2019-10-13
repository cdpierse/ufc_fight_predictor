import os
import pandas as pd
from processor import ProductionProcessor, ProductionStatsProcessor
from utils import r2
from tensorflow import keras
import sys
import numpy as np


class Predict:

    def __init__(self, stats_model=None, winner_model=None):
        # the above params are not yet coded.
        self.pp = ProductionProcessor()
        self.get_fighters()
        self.set_feature_names()
        self.stats_prediction_df = pd.DataFrame(columns=self.stats_feature_names)

        self.pp.read()

    def get_fighters(self):
        filedir = os.path.join(
            os.getcwd(), 'Fight_Predictor', 'Data', 'Scraped_Data', 'scraped_fighters.csv')
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
        self.stats_feature_names = np.load(stats_dir)['feature_names']
        self.stats_target_names = np.load(stats_dir)['fight_stats_columns']

    def get_fighter_data(self, fighter_name):
        return self.fighters[self.fighters.fighter_name == fighter_name]

    def get_fighter_pair_stats(self, pair):
        self.f1_stats = self.get_fighter_data(pair[0])
        self.f2_stats = self.get_fighter_data(pair[1])
        # if isinstance(fighter_pairs, list):
        #     for pairing in fighter_pairs:
        #         self.f1_stats = self.get_fighter_data(pairing[0])
        #         self.f2_stats = self.get_fighter_data(pairing[1])

        # else:
        #     print('fighter_pairs is not list')

    def create_stats_df(self, fighter_pairs):
        if isinstance(fighter_pairs, list):
            for pair in fighter_pairs:
                self.get_fighter_pair_stats(pair)
                prefixes = ['f1', 'f2']
                temp_df = pd.DataFrame(columns=self.stats_prediction_df.columns)

                for prefix in prefixes:            
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
                self.stats_prediction_df = self.stats_prediction_df.append(temp_df, ignore_index=True)
                print(self.stats_prediction_df)
        else:
                print('fighter_pairs is not of type <list>')


p = Predict()
fight_pair = [('Conor McGregor', 'Nate Diaz'), ('Daniel Cormier', 'Conor McGregor')]
#p.get_fighter_pair_stats(fight_pair)
p.create_stats_df(fight_pair)
# print(p.get_fighter_data('Conor McGregor'))
# print(p.stats_feature_names)
