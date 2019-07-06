import os

import pandas as pd

from preprocess_data import FightDataPreprocessor
from utils import r2
from tensorflow import keras

class GetPredictions:
    
    def __init__(self):

        self.fdp = FightDataPreprocessor()
        self.fighters = self.fdp.get_fighters()
        self.fdp.get_fighter_bouts()

        with open('fight_stats_feature_names.txt') as f:
            content = f.readlines()

        self.stats_feature_names = [x.strip() for x in content]

        with open('winner_feature_names.txt') as f:
            content = f.readlines()
        
        self.winner_feature_names = [x.strip() for x in content]
        
        self.prediction_df = pd.DataFrame(columns=self.stats_feature_names) == 0

    def get_fighter_details(self,fighter_name):
        return self.fighters[self.fighters.fighter_name == fighter_name]
    
    def search_partial_fighter_name(self,fighter_name):
        return self.fighters[self.fighters.fighter_name.str.contains(fighter_name)].iloc[0]

    def manual_stats_entry(self):
        """Will allow user to input a set of manual data if a fighter does not exist currently in the db
        """
        pass

    def populate_fighter_df(self,fighter,prefix):
        self.prediction_df.fighter1 = 0
        self.prediction_df.fighter2 = 1
        
        df_structure = {
                        'date_of_birth': prefix +'_dob',
                        'fighter_record':prefix +'_record',
                        'height': prefix +'_height',
                        'reach': prefix +'_reach',
                        'sapm': prefix +'_sapm',
                        'slpm': prefix +'_slpm',
                        'stance':prefix +'_stance',
                        'strike_acc':prefix +'_stk_acc', 
                        'strike_def': prefix + '_stk_def', 
                        'sub_avg': prefix +'_sub_avg',
                        'td_acc': prefix + '_td_acc', 
                        'td_avg': prefix +'_td_avg', 
                        'td_def': prefix +'_td_def', 
                        'weight': prefix +'_weight'
                        }  
            
        for key,value in df_structure.items():
            self.prediction_df[value] = fighter[key].values

    def process_fight(self):
        return self.fdp.data_pipeline_fighter_stats_prediction(self.prediction_df)

    def process_winner(self):
        return self.fdp.data_pipeline_winner_prediction(self.prediction_df)
             
    def create_fighter_dataframe(self, fighter1, fighter2,weight_class):
        """
        Enter manual weight classes depending on what weight the bout is taking place at
        Weight Class Encodings:
            "Women's Strawweight" : 0
            "Women's Flyweight": 1
            "Women's Bantamweight" : 2
            "Women's Featherweight" : 3
            "Flyweight" : 4
            "Bantamweight": 5
            "Featherweight": 6
            "Lightweight": 7
            "Welterweight": 8
            "Middleweight": 9
            "Light Heavyweight": 10
            "Heavyweight": 11
            "Super Heavyweight": 12
            "Open Weight": 13
            "Catch Weight" : 14
        """
        self.populate_fighter_df(fighter1,'f1')
        self.populate_fighter_df(fighter2,'f2')
        self.prediction_df.weight_class =  weight_class
    
    def predict_bout_stats(self):
        scaled,self.prediction_df = self.process_fight()

        current_dir = os.path.join(os.getcwd(),'Fight_Predictor')
        filepath = os.path.join(current_dir,'Saved_Models','Fight_Stats_Models','fighter_stats.h5')

        model = keras.models.load_model(filepath,custom_objects={'r2': r2})

        return model.predict(scaled)

    def predict_bout_winner(self):
        scaled = self.process_winner()

        current_dir = os.path.join(os.getcwd(),'Fight_Predictor')
        filepath = os.path.join(current_dir,'Saved_Models','Winner_Prediction_Models','bout_winner.h5')

        model = keras.models.load_model(filepath)
        implied_abs_probability = self.calculate_implied_probability(model.predict(scaled)[0])
        print(f'Implied Probability is {implied_abs_probability[0]}')

        return model.predict_classes(scaled)
       
    def create_final_df(self):
        """predicts what the stats will be for a given bout, inserts that data into the final 
        """

        results = gp.predict_bout_stats()
        predictor_cols = [ 'pass_stat_f1', 'pass_stat_f2', 'str_stat_f1', 'str_stat_f2',
                            'sub_stat_f1', 'sub_stat_f2', 'td_stat_f1', 'td_stat_f2']

        for prediction, col_name in zip(results[0],predictor_cols):
            if 'f1' in col_name:
                self.prediction_df[col_name] = prediction
            else:
                self.prediction_df[col_name] = prediction

        self.prediction_df = self.prediction_df[self.winner_feature_names]
    def calculate_implied_probability(self,model_output):
        if model_output < 0.50:
            return 1 - model_output
        else:
            return (model_output)

            
if __name__ == ('__main__'):
    gp = GetPredictions()
    fighter1_name = 'Gilbert Melendez'
    fighter2_name = 'Arnold Allen' 
    fighter1 = gp.get_fighter_details(fighter1_name)
    fighter2 = gp.get_fighter_details(fighter2_name)
   
    gp.create_fighter_dataframe(fighter1,fighter2,5)
    gp.create_final_df()
    
    result = gp.predict_bout_winner()
    if result[0] == 0:
        print(f'Predicted Winner is {fighter1_name}')
    else:
        print(f'Predicted Winner is {fighter2_name}')



    
