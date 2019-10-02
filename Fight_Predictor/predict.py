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
        pp = ProductionProcessor()
        self.get_fighters()
        pp.read()

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
        self.stats_feature_names = np.load(stats_dir)['fight_stats_columns']


p = Predict()
p.get_fighters()
p.set_feature_names()
