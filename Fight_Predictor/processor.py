import os
import pandas as pd
import numpy as np
import math


class Processor:

    ORDERED_WEIGHT_CLASSES = [
        "Women's Strawweight", "Women's Flyweight", "Women's Bantamweight",
        "Women's Featherweight", "Flyweight", "Bantamweight", "Featherweight",
        "Lightweight", "Welterweight", "Middleweight", "Light Heavyweight",
        "Heavyweight", "Super Heavyweight", "Open Weight", "Catch Weight"
    ]

    def __init__(self, state=None):
        if state is None:
            self.state = 'train'
        else:
            self.state = 'production'
        self.base_dir = os.path.join(os.getcwd(), 'Fight_Predictor')

    def read(self):
        filepath = os.path.join(
            self.base_dir, 'Data', 'Scraped_Data', 'fighters_bouts_joined.csv')
        # fight bouts is our primary data source for storing fighter and bout specific info
        self.fight_bouts = pd.read_csv(filepath)

    def drop_unused_columns(self):

        with open(os.path.join(self.base_dir, 'Files', 'drop_columns.txt')) as f:
            contents = f.readlines()
        contents = [x.strip() for x in contents]

        for column in contents:
            if column in self.fight_bouts.columns:
                self.fight_bouts = self.fight_bouts.drop(columns=[column])
            else:
                print('{column} is not in fight_bouts')

    def shuffle_winner_positions(self):
        """
        This method handles all of the processes 
        for shuffling the winners in the df and rearranging
        all the columns in the df to match the shuffle. 

        The functinality is quite sensitive to mistakes as this 
        associates the correct values for every bout to be predicted. 
        """

        def index_shuffle(fight_bouts):
            random_winner_index = np.random.choice(len(self.fight_bouts),
                                                   size=math.ceil(
                                                       len(self.fight_bouts)/2),
                                                   replace=False)
            return random_winner_index

        def get_column_names(column_prefix):
            column_names = [
                col for col in self.fight_bouts.columns if column_prefix in col]
            return column_names

        def get_column_index(column_names):
            columns_index = []
            [columns_index.append(self.fight_bouts.columns.get_loc(col))
             for col in self.fight_bouts.columns if col in column_names]
            return columns_index 

        def rearrange_data_to_col_index(col_index1, col_index2, fb_copy=None):
            self.fight_bouts.iloc[random_winner_index,
                                  col_index1] = self.fight_bouts.iloc[random_winner_index, col_index2].values

            self.fight_bouts.iloc[random_winner_index,
                                  col_index2] = fb_copy.iloc[random_winner_index, col_index1].values

        random_winner_index = index_shuffle(self.fight_bouts)

        f1_index = self.fight_bouts.columns.get_loc('fighter1')
        f2_index = self.fight_bouts.columns.get_loc('fighter2')

        self.fight_bouts.iloc[random_winner_index,
                              [f1_index, f2_index]] = self.fight_bouts.iloc[random_winner_index, [f2_index, f1_index]].values
        self.fight_bouts['winner'].iloc[random_winner_index] = self.fight_bouts['fighter2'].iloc[random_winner_index]

        fighter1_columns = get_column_names('f1')
        fighter2_columns = get_column_names('f2')

        fighter1_col_index = get_column_index(fighter1_columns)
        fighter2_col_index = get_column_index(fighter2_columns)

        fight_bouts_copy = self.fight_bouts.copy()

        rearrange_data_to_col_index(fighter1_col_index,fighter2_col_index,fight_bouts_copy)

    def main(self):

        self.read()
        self.drop_unused_columns()
        self.shuffle_winner_positions()


class StatsProcessor(Processor):

    def __init__(self):
        super().__init__(self)

    def read(self):
        filepath = os.path.join(
            self.base_dir, 'Data', 'Scraped_Data', 'scraped_fighters.csv')
        return pd.read_csv(filepath)


if __name__ == "__main__":
    p = Processor()
    p.main()
