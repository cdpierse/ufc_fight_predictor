from preprocess_data  import FightDataPreprocessor
import pandas  as pd


class RetrieveFighters(FightDataPreprocessor):
    
    def __init__(self):
        fdp = FightDataPreprocessor()
        self.fighters = fdp.get_fighters()

        fdp.get_fighter_bouts()
        self.feature_names = fdp.feature_names
        self.prediction_df = pd.DataFrame(columns=self.feature_names)


    def get_fighter_details(self,fighter_name):
        return self.fighters[self.fighters.fighter_name == fighter_name]
    
    def search_partial_fighter_name(self,fighter_name):
        return self.fighters[self.fighters.fighter_name.str.contains(fighter_name)].iloc[0]

    def manual_stats_entry(self):
        """Will allow user to input a set of manual data if a fighter does not exist currently in the db
        """
        pass

    def create_fighter_df(self,fighter):
        prefix = 'f1'

        df_structure = {'date_of_birth': prefix +'_dob',
                        'fighter_name':'fighter1',
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
        
        print(self.prediction_df.iloc[0])
            
        
   

       
    



rf = RetrieveFighters()
fighter = rf.get_fighter_details('Conor McGregor')
rf.create_fighter_df(fighter)
#print(rf.search_partial_fighter_name('Dodson').columns)