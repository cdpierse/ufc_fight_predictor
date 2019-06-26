from preprocess_data  import FightDataPreprocessor
import pandas  as pd


class RetrieveFighters(FightDataPreprocessor):
    
    def __init__(self):
        self.fdp = FightDataPreprocessor()
        self.fighters = self.fdp.get_fighters()


        self.fdp.get_fighter_bouts()

        with open('fight_stats_feature_names.txt') as f:
            content = f.readlines()
        
        self.feature_names = [x.strip() for x in content]
        self.prediction_df = pd.DataFrame(columns=self.feature_names) == 0
  
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
        df_structure = {'date_of_birth': prefix +'_dob',
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
        self.fdp.data_pipeline_fighter_stats_prediction(self.prediction_df)
                
    def create_fighter_df(self, fighter1, fighter2):
        self.populate_fighter_df(fighter1,'f1')
        self.populate_fighter_df(fighter2,'f2')


if __name__ == ('__main__'):
    rf = RetrieveFighters()
    fighter1 = rf.get_fighter_details('Conor McGregor')
    fighter2 =  rf.get_fighter_details('Jose Aldo')
    rf.create_fighter_df(fighter1,fighter2)
    rf.process_fight()
