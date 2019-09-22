import math
import os
import datetime as dt
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import re

pd.set_option("mode.chained_assignment", None)


ORDERED_WEIGHT_CLASSES = [
    "Women's Strawweight",
    "Women's Flyweight",
    "Women's Bantamweight",
    "Women's Featherweight",
    "Flyweight",
    "Bantamweight",
    "Featherweight",
    "Lightweight",
    "Welterweight",
    "Middleweight",
    "Light Heavyweight",
    "Heavyweight",
    "Super Heavyweight",
    "Open Weight",
    "Catch Weight",
]


class Processor:

    def __init__(self, state=None):
        if state is None:
            self.state = "train"
        else:
            self.state = "production"
        self.base_dir = os.path.join(os.getcwd(), "Fight_Predictor")

    def read(self):
        filepath = os.path.join(
            self.base_dir, "Data", "Scraped_Data", "fighters_bouts_joined.csv"
        )
        # fight bouts is our primary data source for storing fighter and bout specific info
        self.fight_bouts = pd.read_csv(filepath)

    def drop_unused_columns(self):

        with open(os.path.join(self.base_dir, "Files", "drop_columns.txt")) as f:
            contents = f.readlines()
        contents = [x.strip() for x in contents]

        for column in contents:
            if column in self.fight_bouts.columns:
                self.fight_bouts = self.fight_bouts.drop(columns=[column])
            else:
                print("{column} is not in fight_bouts")

    def shuffle_winner_positions(self):
        """
        This method handles all of the processes
        for shuffling the winners in the df and rearranging
        all the columns in the df to match the shuffle.

        The functinality is quite sensitive to mistakes as this
        associates the correct values for every bout to be predicted.
        """

        def index_shuffle(fight_bouts):
            random_winner_index = np.random.choice(
                len(self.fight_bouts),
                size=math.ceil(len(self.fight_bouts) / 2),
                replace=False,
            )
            return random_winner_index

        def get_column_names(column_prefix):
            column_names = [
                col for col in self.fight_bouts.columns if column_prefix in col
            ]
            return column_names

        def get_column_index(column_names):
            columns_index = []
            [
                columns_index.append(self.fight_bouts.columns.get_loc(col))
                for col in self.fight_bouts.columns
                if col in column_names
            ]
            return columns_index

        def rearrange_data_to_col_index(col_index1, col_index2, fb_copy=None):
            self.fight_bouts.iloc[
                random_winner_index, col_index1
            ] = self.fight_bouts.iloc[random_winner_index, col_index2].values

            self.fight_bouts.iloc[random_winner_index, col_index2] = fb_copy.iloc[
                random_winner_index, col_index1
            ].values

        random_winner_index = index_shuffle(self.fight_bouts)

        f1_index = self.fight_bouts.columns.get_loc("fighter1")
        f2_index = self.fight_bouts.columns.get_loc("fighter2")

        self.fight_bouts.iloc[random_winner_index, [
            f1_index, f2_index]] = self.fight_bouts.iloc[random_winner_index, [f2_index, f1_index]].values

        self.fight_bouts["winner"].iloc[random_winner_index] = self.fight_bouts[
            "fighter2"].iloc[random_winner_index]

        fighter1_columns = get_column_names("f1")
        fighter2_columns = get_column_names("f2")

        fighter1_col_index = get_column_index(fighter1_columns)
        fighter2_col_index = get_column_index(fighter2_columns)

        fight_bouts_copy = self.fight_bouts.copy()

        rearrange_data_to_col_index(
            fighter1_col_index, fighter2_col_index, fight_bouts_copy
        )

    def process_categorical_columns(self):

        columns_with_dashes = ["f1_dob", "f2_dob", "f1_height", "f2_height"]
        dateime_columns = ["event_date", "f1_dob", "f2_dob"]

        def replace_dashes(columns):
            for column in columns:
                self.categorical_data.loc[
                    self.categorical_data[column] == "--", column] = None

        def column_to_datetime(columns):
            for column in columns:
                self.categorical_data[column] = pd.to_datetime(
                    self.categorical_data[column]
                )

        def make_weight_classes_ordinal():
            self.categorical_data["weight_class"] = self.categorical_data.weight_class.astype(
                CategoricalDtype(
                    categories=ORDERED_WEIGHT_CLASSES, ordered=True)
            ).cat.codes

        def calculate_age_at_fight(fighter_prefix):
            if self.state == 'production':
                self.categorical_data[fighter_prefix + '_ageAtFight'] = (
                    dt.datetime.now() - self.categorical_data[fighter_prefix + '_dob']).dt.days
            else:
                self.categorical_data[fighter_prefix + '_ageAtFight'] = (
                    self.categorical_data.event_date - self.categorical_data[fighter_prefix + '_dob']).dt.days

        def parse_fighter_height(height):
            if height:
                if '"' in height:
                    height = height.replace('"', '')
                ht = height.split("' ")
                ft = float(ht[0])
                inch = float(ht[1])

                return (12 * ft) + inch
            else:
                pass

        def one_hot_encode_stances():
            stances = ['f1_stance', 'f2_stance']
            for stance in stances:
                self.categorical_data = self.categorical_data.join(
                    pd.get_dummies(self.categorical_data[stance], prefix=stance))

            self.categorical_data = self.categorical_data.drop(
                columns=['f1_stance', 'f2_stance', 'f1_dob', 'f2_dob', 'event_date'])

        def encode_fighters():
            self.categorical_data['winner'] = (
                self.categorical_data['fighter2'] == self.categorical_data['winner']).astype('int')
            self.categorical_data['fighter1'] = 0
            self.categorical_data['fighter2'] = 1

        def rejoin_dataframes():
            drop_columns = self.categorical_data.columns
            [self.fight_bouts.drop(columns=[x],inplace =True)
             for x in drop_columns if x in self.fight_bouts.columns]

            self.fight_bouts = pd.concat(
                [self.fight_bouts, self.categorical_data], axis=1)

        self.categorical_data = self.fight_bouts.select_dtypes(
            include="object")

        replace_dashes(columns_with_dashes)
        column_to_datetime(dateime_columns)
        make_weight_classes_ordinal()

        fighter_prefixes = ['f1', 'f2']
        [calculate_age_at_fight(f) for f in fighter_prefixes]

        self.parse_fighter_records()  # maybe this goes into main function

        heights = ['f1_height', 'f2_height']
        for height in heights:
            self.categorical_data[height] = self.categorical_data[height].apply(
                lambda x: parse_fighter_height(x))

        one_hot_encode_stances()
        encode_fighters()
        rejoin_dataframes()

    def parse_fighter_records(self):

        self.categorical_data = self.categorical_data.replace(
            'Record: ', "", regex=True)

        def apply_split_record(fighter_record_name):
            self.record_index = 0

            if fighter_record_name == 'f1_record':
                prefix = 'f1'
            else:
                prefix = 'f2'

            self.categorical_data.apply(lambda x: split_record(
                x[fighter_record_name], prefix), axis=1)

        def split_record(row, prefix):

            win, loss, draw = row.split('-')
            if 'NC' in draw:
                draw = draw.split('(')
                nc = re.sub('[^0-9]', '', draw[1])
                draw = draw[0]
            else:
                nc = 0

            win, loss, draw, nc = int(win), int(loss), int(draw), int(nc)

            self.categorical_data.loc[self.record_index, prefix + '_win'] = win
            self.categorical_data.loc[self.record_index,
                                      prefix + '_loss'] = loss
            self.categorical_data.loc[self.record_index,
                                      prefix + '_draw'] = draw
            self.categorical_data.loc[self.record_index, prefix + '_nc'] = nc
            self.categorical_data.loc[self.record_index,
                                      prefix + '_ratio'] = (win / (win + loss))
            self.record_index += 1

        records = ['f1_record', 'f2_record']
        [apply_split_record(r) for r in records]

        self.catergorical_data = self.categorical_data.drop(
            columns=['f1_record', 'f2_record'], inplace=True)  # not working

    def main(self):
        self.read()
        self.drop_unused_columns()
        self.shuffle_winner_positions()
        self.process_categorical_columns()


class StatsProcessor(Processor):
    def __init__(self):
        super().__init__(self)

    def read(self):
        filepath = os.path.join(
            self.base_dir, "Data", "Scraped_Data", "scraped_fighters.csv"
        )
        return pd.read_csv(filepath)


if __name__ == "__main__":
    p = Processor()
    p.main()
