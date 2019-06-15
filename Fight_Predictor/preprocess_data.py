import math
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

pd.set_option('mode.chained_assignment', None)

class FightDataPreprocessor:
    X_train = None
    y_train = None
    X_test = None 
    y_test = None
    scaler = None                    
    data_dir_name = None

    rand_winner_index = []

    weight_classes_ordered = [
                            "Women's Strawweight","Women's Flyweight","Women's Bantamweight",
                            "Women's Featherweight", "Flyweight", "Bantamweight", "Featherweight",
                            "Lightweight","Welterweight", "Middleweight","Light Heavyweight",
                            "Heavyweight", "Super Heavyweight", "Open Weight","Catch Weight"
                            ]

    fight_stats_targets = [
                            'pass_stat_f1', 'pass_stat_f2', 'str_stat_f1', 'str_stat_f2',
                           'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 'td_stat_f2'
                        ]
    

    def data_pipeline_generic(self):

        print('Starting data preprocessing pipeline...')

        fightbouts = self.get_fighter_bouts()
        fightbouts = self.drop_unused_columns(fightbouts)

        fightbouts = self.shuffle_winner_positions(fightbouts)

        fighter1_columns = self.get_column_names('f1',fightbouts)
        fighter2_columns = self.get_column_names('f2',fightbouts)

        fighter1_col_index = self.get_column_index(fightbouts,fighter1_columns)
        fighter2_col_index = self.get_column_index(fightbouts,fighter2_columns)

        fightbouts_copy = fightbouts.copy()
        
        fightbouts = self.rearrange_data_to_col_index(fightbouts,
                                        fighter1_col_index,
                                        fighter2_col_index)

        fightbouts = self.rearrange_data_to_col_index(fightbouts,
                                        fighter1_col_index,
                                        fighter2_col_index,
                                        fightbouts_copy)
        
        categorical_fbout = self.categorical_data_pipeline(fightbouts)

        fightbouts = self.join_dataframes(categorical_fbout,self.remove_catergorical_columns(fightbouts))

        return fightbouts

    def data_pipeline_fighter_stats_prediction(self):
        
        self.data_dir_name = 'fighter_stats_prediction_data'

        fightbouts = self.data_pipeline_generic()

        targets = fightbouts[self.fight_stats_targets]

        fightbouts = fightbouts.drop(columns = targets.columns)

        #for now we are not including the below 
        #fightbouts = self.standard_scale_dataframe(fightbouts)
        
        fightbouts = self.standard_scale_dataframe(fightbouts)
        fightbouts = self.impute_dataframe(fightbouts)

        self.train_test_split_regular(fightbouts,targets)

        self.train_test_to_csv(self.X_train,'X_train')
        self.train_test_to_csv(self.y_train,'y_train')
        self.train_test_to_csv(self.X_test,'X_test')
        self.train_test_to_csv(self.y_test,'y_test')  

        print('Completed data preprocessing pipeline for fight statistics prediction...')


    def data_pipeline_winner_prediction(self):

        self.data_dir_name = 'winner_prediction_data'

        fightbouts = self.data_pipeline_generic()

        target = self.get_winners_target(fightbouts)
        
        fightbouts = fightbouts.drop(columns =["winner"])
      
        fightbouts = self.standard_scale_dataframe(fightbouts)
        fightbouts  = self.impute_dataframe(fightbouts)

        self.strata_shuffle_data(fightbouts,target)

        self.train_test_to_csv(self.X_train,'X_train')
        self.train_test_to_csv(self.y_train,'y_train')
        self.train_test_to_csv(self.X_test,'X_test')
        self.train_test_to_csv(self.y_test,'y_test')

        print('Completed data preprocessing pipeline for winner prediction...')


    def categorical_data_pipeline(self,fight_bout_data):

        categorical_fbout = self.create_categorical_dataframe(fight_bout_data)
        bad_value_columns = ['f1_dob','f2_dob','f1_height','f2_height']

        for column in bad_value_columns:
            categorical_fbout = self.remove_bad_values(categorical_fbout,column)
        
        dateime_columns = ['event_date','f1_dob','f2_dob']
        for column in dateime_columns:
            categorical_fbout = self.set_column_to_datetime(categorical_fbout,column)
        
        categorical_fbout = self.make_weight_classes_ordinal(categorical_fbout)

        categorical_fbout = self.calculate_age_at_fight(categorical_fbout,'f1')
        categorical_fbout = self.calculate_age_at_fight(categorical_fbout,'f2')

        categorical_fbout = self.parse_fighter_record(categorical_fbout)

        lambda_fn = lambda x: self.parse_fighter_height(x)
        
        categorical_fbout['f1_height'] = categorical_fbout['f1_height'].apply(lambda_fn)
        categorical_fbout['f2_height'] = categorical_fbout['f2_height'].apply(lambda_fn)

        categorical_fbout = self.one_hot_encode(categorical_fbout)

        categorical_fbout = self.set_winner_to_last_column(categorical_fbout)


        categorical_fbout = self.binary_encode_fighters(categorical_fbout)

        return categorical_fbout


    def get_fighters(self):
        try:
            fighters = pd.read_csv('Fights_scraper/spiders/scraped_fighters.csv')
        except IOError:
            sys.exit('Unable to read Fighters file from disk. Exiting.')
        return fighters

    def get_bouts(self):
        try:
            bouts = pd.read_csv('Bouts_Scraper/bouts_scraped/bouts_scraped/spiders/scraped_bouts.csv')
        except:
            sys.exit('Unable to read Bouts file from disk. Exiting.')
        return bouts

    def get_fighter_bouts(self):
        try:
            fighter_bouts =  pd.read_csv('Fight_Predictor/fighters_bouts_joined.csv')
        except:
            sys.exit('Unable to read Fighter Bouts Joined from disk. Exiting.')
        return fighter_bouts

    def drop_unused_columns(self,fight_bout_data):

    
        columns = ['round','time','win_method_finish','win_method_type','event_attendence']
        try:
            fight_bout_data = fight_bout_data.drop(columns= columns)
        except IOError: 
            print("Couldn't drop assigned columns from dataframe")
        return fight_bout_data
    
    def random_shuffle_winner_index(self,fight_bout_data):
        self.rand_winner_index = np.random.choice(len(fight_bout_data),
                                  size= math.ceil(len(fight_bout_data)/2),
                                  replace = False)
    
    def shuffle_winner_positions(self,fight_bout_data):
        self.random_shuffle_winner_index(fight_bout_data)

        f1_index = fight_bout_data.columns.get_loc('fighter1')
        f2_index = fight_bout_data.columns.get_loc('fighter2')

        fight_bout_data.iloc[self.rand_winner_index,[f1_index,f2_index]] = fight_bout_data.iloc[self.rand_winner_index,[f2_index,f1_index]].values
        fight_bout_data['winner'].iloc[self.rand_winner_index] = fight_bout_data['fighter2'].iloc[self.rand_winner_index]

        return fight_bout_data

    def get_column_names(self,column_prefix,fight_bout_data):
        column_names = [col for col in fight_bout_data.columns if column_prefix in col]
        return column_names
        

    def get_column_index(self,fight_bout_data,column_names):
        columns_index = []
        for col in fight_bout_data.columns:
            if col in column_names:
                columns_index.append(fight_bout_data.columns.get_loc(col))

        return columns_index
    
    def rearrange_data_to_col_index(self,fight_bout_data,col_index1,col_index2,fb_copy = None):
        #when you implement this remember that a copy is needed
        if fb_copy is None:
            fight_bout_data.iloc[self.rand_winner_index,col_index1] = fight_bout_data.iloc[self.rand_winner_index,col_index2].values

        else:
            fight_bout_data.iloc[self.rand_winner_index,col_index2] = fb_copy.iloc[self.rand_winner_index,col_index1].values
            
        
        return fight_bout_data
    
    def create_categorical_dataframe(self,fight_bout_data):
        categorical_data = fight_bout_data.select_dtypes(include='object')
        return categorical_data

    def remove_catergorical_columns(self,fight_bout_data):
        cat_columns = fight_bout_data.select_dtypes(include='object').columns
        fight_bout_data = fight_bout_data.drop(columns = cat_columns)
        return fight_bout_data

    def remove_bad_values(self,categorical_data,column_name):
        categorical_data[column_name] = categorical_data[column_name].replace('--',None)
        return categorical_data
    
    def set_column_to_datetime(self,categorical_data,column):
        categorical_data[column] = pd.to_datetime(categorical_data[column])
        return categorical_data
    
    def make_weight_classes_ordinal(self,categorical_data):

        categorical_data["weight_class"] = categorical_data.weight_class.astype(
            CategoricalDtype(categories=self.weight_classes_ordered,ordered= True)).cat.codes

        return categorical_data 
    
    def calculate_age_at_fight(self,categorical_data,fighter_prefix):
        categorical_data[fighter_prefix + '_ageAtFight'] = (categorical_data.event_date- categorical_data[fighter_prefix+'_dob']).dt.days
        return categorical_data 
    
    def parse_fighter_record(self,categorical_data):

        categorical_data = categorical_data.replace('Record: ',"",regex=True)
        
        categorical_data['f1_win'],categorical_data['f1_loss'],categorical_data['f1_draw'],categorical_data['f1_nc'] = 0,0,0,0
        categorical_data['f2_win'],categorical_data['f2_loss'],categorical_data['f2_draw'],categorical_data['f2_nc'] = 0,0,0,0

        categorical_data['f1_win'],categorical_data['f1_loss'],categorical_data['f1_draw'],categorical_data['f1_nc'] = \
             self.apply_split_record(categorical_data,'f1_record')

        categorical_data['f2_win'],categorical_data['f2_loss'],categorical_data['f2_draw'],categorical_data['f2_nc'] = \
            self.apply_split_record(categorical_data,'f2_record')
        
        categorical_data =  categorical_data.drop(columns =['f1_record','f2_record'])

        return categorical_data
    
    def apply_split_record(self,categorical_data,fighter_record_name):
        return zip(*categorical_data.apply(lambda x: self.split_record(x[fighter_record_name]), axis=1))

    def split_record(self,row):

        win,loss, draw = row.split('-')
        nc= 0
        if 'NC' in draw:       
            draw = draw.split('(')
            nc = re.sub('[^0-9]','', draw[1])
            draw = draw[0]
        else:
            nc = 0     
            
        win,loss, draw, nc = int(win),int(loss), int(draw), int(nc)
            
        return  win,loss,draw,nc
    
    def set_winner_to_last_column(self,categorical_data):
        columns = list(categorical_data.columns.values)
        columns.pop(columns.index('winner'))
        categorical_data = categorical_data[columns+['winner']]

        return categorical_data
    
    def parse_fighter_height(self,height):
        ht = height.split("' ")
        ft = float(ht[0])
        inch = float(ht[1])

        return (12*ft) + inch
    
    def one_hot_encode(self,categorical_data):
        stances = ['f1_stance','f2_stance']
        for stance in stances:
            categorical_data = categorical_data.join(pd.get_dummies(categorical_data[stance],prefix=stance))
        
        categorical_data = categorical_data.drop(columns=['f1_stance','f2_stance','f1_dob','f2_dob','event_date'])
        return categorical_data
    
    def binary_encode_fighters(self,categorical_data):
        categorical_data['winner'] = (categorical_data['fighter2'] == categorical_data['winner']).astype('int')
        categorical_data['fighter1'] = 0
        categorical_data['fighter2'] = 1

        return categorical_data

    def join_dataframes(self,categorical_data,numerical_data):
        joined_data = pd.concat([numerical_data,categorical_data], axis =1)
        return joined_data 

    def get_winners_target(self,fight_bout_data):
        #don't forget to drop the winner column once you do this
        target = fight_bout_data.winner
        return target

    
    def standard_scale_dataframe(self,fight_bout_data):
        fight_bout_data = fight_bout_data.apply(pd.to_numeric)
        #fight_bout_data = pd.to_numeric(fight_bout_data,downcast='float')
        scaler = RobustScaler()
        scaled_data = scaler.fit_transform(fight_bout_data)
        self.scaler = scaler

        return scaled_data
    
    def impute_dataframe(self,fight_bout_data):
        imputer = SimpleImputer(strategy= 'most_frequent',copy= False)
        imputed_data = imputer.fit_transform(fight_bout_data)
        return imputed_data
    
    def strata_shuffle_data(self,fight_bout_data,target):
        sss= StratifiedShuffleSplit(n_splits=20,test_size=0.1,random_state=42)

        for train_index, test_index in sss.split(fight_bout_data, target):
            X_train, X_test = fight_bout_data[train_index], fight_bout_data[test_index]
            y_train, y_test = target[train_index], target[test_index]
        
        self.X_train, self.y_train = X_train, y_train.values
        self.X_test, self.y_test = X_test, y_test.values
    
    def train_test_split_regular(self,fight_bout_data,targets):

        self.X_train,self.X_test,self.y_train,self.y_test = \
             train_test_split(fight_bout_data,targets.values, test_size=0.10, random_state=42)


    def train_test_to_csv(self,file,filename):

        dirName = os.path.join('Fight_Predictor/model_data',self.data_dir_name)
        file_location = os.path.join(dirName, filename+".csv")

        try:
            os.mkdir(dirName)
            print("Directory " , dirName ,  " Created ")
            np.savetxt(file_location,file,delimiter= ',')
        except FileExistsError:
            print("Directory " , dirName ,  " already exists") 
            np.savetxt(file_location,file,delimiter= ',')
       

fdp = FightDataPreprocessor()
fdp.data_pipeline_winner_prediction()
fdp.data_pipeline_fighter_stats_prediction()
# scaler = fdp.scaler
# print(fdp.y_test)
#print(scaler.inverse_transform(fdp.y_test))
