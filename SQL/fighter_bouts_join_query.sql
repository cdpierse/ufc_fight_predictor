CREATE TABLE temp_fighter_bout AS 
	  SELECT b.*, 
	  f.date_of_birth as f1_dob,
	  f.fighter_record as f1_record,
	  f.height as f1_height,
	  f.reach as f1_reach,
	  f.sapm as f1_sapm,
	  f.slpm as f1_slpm,
	  f.stance as f1_stance,
	  f.strike_acc as f1_stk_acc,
	  f.strike_def as f1_stk_def,
	  f.sub_avg as f1_sub_avg,
	  f.td_acc as f1_td_acc,
	  f.td_avg as f1_td_avg,
	  f.td_def as f1_td_def,
	  f.weight as f1_weight
	  
      FROM bouts as b
      JOIN fighters as f
      ON f.fighter_name = b.fighter1


CREATE TABLE fighter_bouts_joined AS 
	  SELECT tfb.*, 
	  f.date_of_birth as f2_dob,
	  f.fighter_record as f2_record,
	  f.height as f2_height,
	  f.reach as f2_reach,
	  f.sapm as f2_sapm,
	  f.slpm as f2_slpm,
	  f.stance as f2_stance,
	  f.strike_acc as f2_stk_acc,
	  f.strike_def as f2_stk_def,
	  f.sub_avg as f2_sub_avg,
	  f.td_acc as f2_td_acc,
	  f.td_avg as f2_td_avg,
	  f.td_def as f2_td_def,
	  f.weight as f2_weight
	  
      FROM temp_fighter_bout as tfb
      JOIN fighters as f
      ON f.fighter_name = tfb.fighter2

