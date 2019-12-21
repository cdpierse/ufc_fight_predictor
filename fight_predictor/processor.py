import datetime as dt
import math
import os
import re

import joblib
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler

pd.set_option("mode.chained_assignment", None)


class Processor:

    def __init__(self):
        self.scaler_name = 'win_scaler'
        self.imputer_name = 'win_imputer'
        self.base_dir = os.path.join(os.getcwd())

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
                print(f"{column} not dropped as it is not in dataframe")

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

        def rearrange_data_to_col_index(col_index1, col_index2, fb_copy):
            self.fight_bouts.iloc[random_winner_index, col_index1] = self.fight_bouts.iloc[
                random_winner_index, col_index2].values

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

    def process_categorical_columns(self, state='training'):

        columns_with_dashes = ["f1_dob", "f2_dob", "f1_height", "f2_height"]

        if state == 'production':
            dateime_columns = ["f1_dob", "f2_dob"]
        else:
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

        def calculate_age_at_fight(fighter_prefix):
            if state == 'production':
                self.categorical_data[fighter_prefix + '_ageAtFight'] = (
                    dt.datetime.now() - self.categorical_data[fighter_prefix + '_dob']).dt.days / 365.5
            else:
                self.categorical_data[fighter_prefix + '_ageAtFight'] = (
                    self.categorical_data.event_date - self.categorical_data[fighter_prefix + '_dob']).dt.days / 365.5

        def one_hot_encode_stances():
            if state == 'production':
                f1_stances = self.categorical_data.f1_stance.values
                f2_stances = self.categorical_data.f2_stance.values
                self.categorical_data.drop(
                    columns=['f1_stance', 'f2_stance', 'f1_dob', 'f2_dob'], inplace=True)
                stance_cols = [col for col in self.categorical_data.columns if 'stance' in col]
                assign_correct_stance_production(f1_stances, f2_stances, stance_cols)
            else:

                stances = ['f1_stance', 'f2_stance']
                for stance in stances:
                    self.categorical_data = self.categorical_data.join(
                        pd.get_dummies(self.categorical_data[stance], prefix=stance))
                     
                self.categorical_data.drop(
                    columns=['f1_stance', 'f2_stance', 'f1_dob', 'f2_dob', 'event_date'], inplace=True)

        def assign_correct_stance_production(f1_stances, f2_stances, stance_cols):
            for i, (f1_stance, f2_stance) in enumerate(zip(f1_stances, f2_stances)):
                matched_f1_stance = match_stance(f1_stance, stance_cols, 'f1')
                matched_f2_stance = match_stance(f2_stance, stance_cols, 'f2')
                if matched_f1_stance is not None:  # if a column was returned
                    self.categorical_data.loc[i, matched_f1_stance] = 1
                    temp_stance_cols = stance_cols.copy()
                    temp_stance_cols.remove(matched_f1_stance)
                    for col in temp_stance_cols[:]:
                        if 'f2' in col:
                            temp_stance_cols.remove(col)
                    self.categorical_data.loc[i, temp_stance_cols] = 0
                    
                else:  # otherwise set all cols in that row to 0 
                    self.categorical_data.loc[i, stance_cols] = 0
                    self.categorical_data.loc[i, ['f1_stance_Orthodox']] = 1  # give them orthodox stance by default

                if matched_f2_stance is not None:
                    self.categorical_data.loc[i, matched_f2_stance] = 1
                    temp_stance_cols = stance_cols.copy()
                    temp_stance_cols.remove(matched_f2_stance)
                    for col in temp_stance_cols[:]:
                        if 'f1' in col:
                            temp_stance_cols.remove(col)
                    self.categorical_data.loc[i, temp_stance_cols] = 0
  
                else:
                    self.categorical_data.loc[i, stance_cols] = 0
                    self.categorical_data.loc[i, ['f2_stance_Orthodox']] = 1  # give them orthodox stance by default

        def match_stance(stance, stance_cols, prefix):
            for col in stance_cols:
                temp_col = col.replace("_", " ").lower()
                if isinstance(stance, str) and stance.lower() in temp_col and prefix in temp_col:
                    return col

        def encode_fighters():
            self.categorical_data['winner'] = (
                self.categorical_data['fighter2'] == self.categorical_data['winner']).astype('int')
            self.categorical_data['fighter1'] = 0
            self.categorical_data['fighter2'] = 1

        def rejoin_dataframes():
            self.fight_bouts = pd.concat(
                [self.fight_bouts, self.categorical_data], axis=1)

        self.categorical_data = self.fight_bouts.select_dtypes(
            include="object")

        drop_columns = self.categorical_data.columns
        [self.fight_bouts.drop(columns=[x], inplace=True)
         for x in drop_columns if x in self.fight_bouts.columns]

        replace_dashes(columns_with_dashes)
        column_to_datetime(dateime_columns)

        fighter_prefixes = ['f1', 'f2']
        [calculate_age_at_fight(f) for f in fighter_prefixes]

        self.parse_fighter_records()  # maybe this goes into main function

        heights = ['f1_height', 'f2_height']
        for height in heights:
            self.categorical_data[height] = self.categorical_data[height].apply(
                lambda x: self.parse_fighter_height(x))

        one_hot_encode_stances()
        if state != 'production':
            encode_fighters()
        rejoin_dataframes()

    def parse_fighter_height(self, height):
        if height:
            if '"' in height:
                height = height.replace('"', '')
            ht = height.split("' ")
            ft = float(ht[0])
            inch = float(ht[1])

            return (12 * ft) + inch
        else:
            pass

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

            # Blocking this out for now, as model seems to lean on wins and losses heavily
            # self.categorical_data.loc[self.record_index,
            #                           prefix + '_win'] = win
            # self.categorical_data.loc[self.record_index,
            #                           prefix + '_loss'] = loss
            self.categorical_data.loc[self.record_index,
                                      prefix + '_draw'] = draw
            self.categorical_data.loc[self.record_index,
                                      prefix + '_nc'] = nc
            self.categorical_data.loc[self.record_index,
                                      prefix + '_ratio'] = (win / (win + loss))
            self.record_index += 1

        records = ['f1_record', 'f2_record']
        [apply_split_record(r) for r in records]

        self.catergorical_data = self.categorical_data.drop(
            columns=['f1_record', 'f2_record'], inplace=True)

    def set_target(self):
        self.target = self.fight_bouts.winner
        self.fight_bouts = self.fight_bouts.drop(
            columns=['winner'])

    def impute(self):

        def save(imputer):
            file_dir = os.path.join(
                self.base_dir, 'Files', 'Transformers', 'Imputers')
            imputer_name = self.imputer_name + '.pkl'
            joblib.dump(imputer, os.path.join(file_dir, imputer_name))

        columns = self.fight_bouts.columns
        imputer = SimpleImputer(strategy='most_frequent', copy=False)
        imputer.fit(self.fight_bouts)
        imputed_data = imputer.transform(self.fight_bouts)
        save(imputer)

        self.fight_bouts = pd.DataFrame(imputed_data, columns=columns)

    def scale(self):

        self.original_values = self.fight_bouts.values
        self.feature_names = self.fight_bouts.columns.tolist()

        def save(scaler):
            file_dir = os.path.join(
                self.base_dir, 'Files', 'Transformers', 'Scalers')
            scaler_name = self.scaler_name + '.pkl'
            joblib.dump(scaler, os.path.join(file_dir, scaler_name))

        scaler = RobustScaler()
        scaler.fit(self.fight_bouts)
        self.fight_bouts = scaler.transform(self.fight_bouts)
        save(scaler)

    def stratify_shuffle(self):
        sss = StratifiedShuffleSplit(
            n_splits=20, test_size=0.1, random_state=42)

        for train_index, test_index in sss.split(self.fight_bouts, self.target):
            X_train, X_test = self.fight_bouts[train_index], self.fight_bouts[test_index]
            y_train, y_test = self.target[train_index], self.target[test_index]

        self.X_train, self.y_train = X_train, y_train.values
        self.X_test, self.y_test = X_test, y_test.values

    def save_train_test_to_file(self, folder, f_stats_cols=None):
        save_loc = os.path.join(self.base_dir, 'Data',
                                'Processed_Data', folder)
        print(f'saving at {save_loc}')
        np.savez_compressed(os.path.join(save_loc, 'data'),
                            x_train=self.X_train,
                            y_train=self.y_train,
                            x_test=self.X_test,
                            y_test=self.y_test,
                            original_values=self.original_values,
                            feature_names=self.feature_names,
                            fight_stats_columns=f_stats_cols)

    def main(self):
        self.read()
        self.drop_unused_columns()
        self.shuffle_winner_positions()
        self.process_categorical_columns()
        self.set_target()
        self.impute()
        self.scale()
        self.stratify_shuffle()
        self.save_train_test_to_file('Fight_Winner')


class StatsProcessor(Processor):
    def __init__(self):
        super().__init__()
        self.scaler_name = 'stats_scaler'
        self.imputer_name = 'stats_imputer'

        self.fight_stats_targets = ['pass_stat_f1', 'pass_stat_f2', 'str_stat_f1',
                                    'str_stat_f2', 'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 'td_stat_f2']

    def set_targets(self):
        self.targets = self.fight_bouts[self.fight_stats_targets]

    def drop_targets_from_df(self):
        self.fight_bouts.drop(columns=self.fight_stats_targets, inplace=True)

    def split_data(self):
        self.X_train, self.X_test, self.y_train, self.y_test = \
            train_test_split(self.fight_bouts, self.targets.values,
                             test_size=0.10, random_state=99)

    def main(self):
        self.read()
        self.drop_unused_columns()
        self.set_targets()
        self.drop_targets_from_df()
        self.shuffle_winner_positions()
        self.process_categorical_columns()
        self.fight_bouts.drop(columns='winner', inplace=True)
        self.impute()
        self.scale()
        self.split_data()
        self.save_train_test_to_file('Fight_Stats', self.fight_stats_targets)


class ProductionProcessor(Processor):
    """ Implementation of Processor for dealing with fight data that
    needs to be processed for use in production/test situations.
    """

    def __init__(self, fight_bouts, columns):
        super().__init__()
        self.fight_bouts = fight_bouts
        self.columns = columns
        
    def win_impute(self):
        imputer_path = os.path.join(
            self.base_dir,
            'Files',
            'Transformers',
            'Imputers',
            'win_imputer' + '.pkl')
        imputer = joblib.load(imputer_path)
        imputed_data = imputer.transform(self.fight_bouts)

        self.fight_bouts = pd.DataFrame(imputed_data, columns=self.fight_bouts.columns)

    def win_scale(self):
        scaler_path = os.path.join(
            self.base_dir,
            'Files',
            'Transformers',
            'Scalers',
            'win_scaler' + '.pkl')
        scaler = joblib.load(scaler_path)
        self.fight_bouts = scaler.transform(self.fight_bouts)
    
    def stats_impute(self):
        imputer_path = os.path.join(
            self.base_dir,
            'Files',
            'Transformers',
            'Imputers',
            'stats_imputer' + '.pkl')
        imputer = joblib.load(imputer_path)
        imputed_data = imputer.transform(self.fight_bouts)

        self.fight_bouts = pd.DataFrame(imputed_data, columns=self.fight_bouts.columns)

    def stats_scale(self):
        scaler_path = os.path.join(
            self.base_dir,
            'Files',
            'Transformers',
            'Scalers',
            'stats_scaler' + '.pkl')
        scaler = joblib.load(scaler_path)
        self.fight_bouts = scaler.transform(self.fight_bouts)
    
    def reindex(self):
        self.fight_bouts = self.fight_bouts.reindex(columns=self.columns)
    
    def winner_main(self):
        self.reindex()
        self.win_impute()
        self.win_scale()
    
    def stats_main(self):
        self.drop_unused_columns()
        self.process_categorical_columns(state='production')
        self.reindex()
        self.stats_impute()
        self.unscaled_df = self.fight_bouts.copy()
        self.stats_scale()

if __name__ == "__main__":
    p = Processor()
    p.main()
    sp = StatsProcessor()
    sp.main()
