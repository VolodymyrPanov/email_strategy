import pandas as pd
import numpy as np

# Getting inputs
inbox_need = pd.read_csv(input("Enter name of the team in plus file:"), usecols=[0,1,2])
team_df = pd.read_csv(input("Enter name of the team hours file:"), usecols=[0,1,2])
inbox_need_deficit = pd.read_csv(input("Enter name of the team in minus file:"), usecols=[0,1,2])

# Fulfilling requirements of teams that have extra capacity
def balance_own_demand(team_df, inbox_need):
    scenario_name_waste = []
    scenario_waste = []
    
# Leaving only teams that have extra capacity
    team_df = team_df[team_df.iloc[:,1].isin(inbox_need.iloc[:,1])]
    team_lst = []
    scenario_name = []
    
# for loops to create multiple scenarios of fulfillment
    for sc in range(len(team_df['team'])):
        result_lst = []
        for inde, row in inbox_need.iterrows():
            result = 0
            for ind in range(len(team_df['team'])):
                if result < row['need'] * 0.95 and team_df['available'][ind] < row['need']:
                    if team_df['region'][ind] == row['region']:
                        result += team_df['available'][ind]
                        team_lst.append(team_df['team'][ind])
                        scenario_name.append(f'Scenario {sc}')
                    else:
                        continue
                else:
                    break
            result_lst.append(abs(row['need'] - result))
        scenario_waste.extend([sum(result_lst)])
        scenario_name_waste.append(f'Scenario {sc}')
        team_df = team_df.reindex(np.roll(team_df.index, shift=1))
        team_df = team_df.reset_index(drop=True)

# Create df that contains team list for each scenario
    sc_result_teams = pd.DataFrame({'Scenario': scenario_name,
                                    'Team': team_lst})

# Create df that contains waste result for each scenario
    sc_result_waste = pd.DataFrame({'Scenario': scenario_name_waste,
                                    'Waste': scenario_waste})
# Getting best scenario
    base_scenario_waste = sc_result_waste[sc_result_waste.iloc[:,1] == min(sc_result_waste.iloc[:,1])]
    base_scenario_teams = sc_result_teams[sc_result_teams.iloc[:,0] == base_scenario_waste.iloc[0][0]]
    team_subset = team_df[~team_df.iloc[:,0].isin(base_scenario_teams.iloc[:,1])]

    return team_subset

# Fulfilling requirements of teams that have capacity deficit
def scenario_creator(inbox_need_deficit):
    team_list = []
    scenario_name = []
    scenario_res_waste = []
    scenario_res_name = []
    inbox_assignment = []
    region_assignment = []
    fulfillment = float(input("Enter fulfilment % for teams in minus:"))
    team_arr = balance_own_demand(team_df=team_df, inbox_need=inbox_need).reset_index()

    for s in range(len(team_arr['team'])):
        result_list = []
        used_teams = []
        for ind, row in inbox_need_deficit.iterrows():
            res = 0
            for i in range(len(team_arr['team'])):
                if res < row['need'] * fulfillment:
                    if team_arr['available'][i] < row['need'] and team_arr['team'][i] not in used_teams:
                        res += team_arr['available'][i]
                        used_teams.append(team_arr['team'][i])
                        team_list.append(team_arr['team'][i])
                        scenario_name.append(f'Scenario {s}')
                        inbox_assignment.append(row['inbox'])
                        region_assignment.append(row['region'])
                    else:
                        continue
                else:
                    break

            result_list.append(abs(row['need'] - res))
        scenario_res_waste.extend([sum(result_list)])
        scenario_res_name.append(f'Scenario {s}')
        team_arr = team_arr.reindex(np.roll(team_arr.index, shift=1))
        team_arr = team_arr.reset_index(drop=True)

    final_sc_team = pd.DataFrame({'Scenario': scenario_name,
                                  'Team': team_list,
                                  'Help_inbox': inbox_assignment,
                                  'Help_region': region_assignment})

    final_sc_waste = pd.DataFrame({'Scenario': scenario_res_name,
                                   'Waste': scenario_res_waste})

    final_scenario_waste = final_sc_waste[final_sc_waste.iloc[:, 1] == min(final_sc_waste.iloc[:, 1])]
    final_scenario_teams = final_sc_team[final_sc_team.iloc[:, 0] == final_scenario_waste.iloc[0][0]]
    return final_scenario_teams

with open('strategy.csv', 'w') as file:
    scenario_creator(inbox_need_deficit=inbox_need_deficit).to_csv(file, sep=',', index=False)
exit()
