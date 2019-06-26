SELECT sb.*, 
	  sf.date_of_birth as f1_dob,
	  sf.fighter_record as f1_record,
	  sf.height as f1_height,
	  sf.reach as f1_reach,
	  sf.sapm as f1_sapm,
	  sf.slpm as f1_slpm,
	  sf.stance as f1_stance,
	  sf.strike_acc as f1_stk_acc,
	  sf.strike_def as f1_stk_def,
	  sf.sub_avg as f1_sub_avg,
	  sf.td_acc as f1_td_acc,
	  sf.td_avg as f1_td_avg,
	  sf.td_def as f1_td_def,
	  sf.weight as f1_weight
	  
INTO temp_fighter_bout  
FROM scraped_bouts as sb
JOIN scraped_fighters as sf
ON sf.fighter_name = sb.fighter1


-------------------------


SELECT tfb.*, 
	  sf.date_of_birth as f2_dob,
	  sf.fighter_record as f2_record,
	  sf.height as f2_height,
	  sf.reach as f2_reach,
	  sf.sapm as f2_sapm,
	  sf.slpm as f2_slpm,
	  sf.stance as f2_stance,
	  sf.strike_acc as f2_stk_acc,
	  sf.strike_def as f2_stk_def,
	  sf.sub_avg as f2_sub_avg,
	  sf.td_acc as f2_td_acc,
	  sf.td_avg as f2_td_avg,
	  sf.td_def as f2_td_def,
	  sf.weight as f2_weight
	  
INTO fighter_bouts_joined_new
FROM temp_fighter_bout as tfb
JOIN scraped_fighters as sf
ON sf.fighter_name = tfb.fighter2

