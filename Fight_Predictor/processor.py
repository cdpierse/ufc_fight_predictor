import os
import pandas as pd
import numpy as np


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
        self.base_dir = os.path.join(os.getcwd(),'Fight_Predictor')

    def read(self):
        filepath = os.path.join(
            self.base_dir, 'Data', 'Scraped_Data', 'fighters_bouts_joined.csv')
        # fight bouts is our primary data source for storing fighter and bout specific info
        self.fight_bouts = pd.read_csv(filepath)
        print(self.fight_bouts.columns)

    def drop_unused_columns(self):

        with open(os.path.join(self.base_dir, 'Files', 'drop_columns.txt')) as f:
            contents = f.readlines()
        contents = [x.strip() for x in contents]
        self.fight_bouts = self.fight_bouts.drop(contents)

    def main(self):

        self.read()
        self.drop_unused_columns()


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
   
