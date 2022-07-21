import pandas as pd
import numpy as np

inbox_need = pd.read_csv('teams_in_plus_18_22_Jul.csv', usecols=[0,1,2])
team_df = pd.read_csv('team_hours_18_22_Jul.csv', usecols=[0,1,2])
inbox_need_deficit = pd.read_csv('teams_in_minus_18_22_Jul.csv', usecols=[0,1,2])

def balance_own_demand(team_df, inbox_need):
    scenario_name_waste = []
    scenario_waste = []
    team_df = team_df[team_df.iloc[:,1].isin(inbox_need.iloc[:,1])]
    team_lst = []
    scenario_name = []
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


    sc_result_teams = pd.DataFrame({'Scenario': scenario_name,
                                    'Team': team_lst})

    sc_result_waste = pd.DataFrame({'Scenario': scenario_name_waste,
                                    'Waste': scenario_waste})

    base_scenario_waste = sc_result_waste[sc_result_waste.iloc[:,1] == min(sc_result_waste.iloc[:,1])]
    base_scenario_teams = sc_result_teams[sc_result_teams.iloc[:,0] == base_scenario_waste.iloc[0][0]]
    team_subset = team_df[~team_df.iloc[:,0].isin(base_scenario_teams.iloc[:,1])]

    return team_subset


def scenario_creator(inbox_need_deficit):
    team_list = []
    scenario_name = []
    scenario_res_waste = []
    scenario_res_name = []
    inbox_assignment = []
    region_assignment = []
    team_arr = balance_own_demand(team_df=team_df, inbox_need=inbox_need).reset_index()
    for s in range(len(team_arr['team'])):
        index = 0
        result_list = []

        for ind, row in inbox_need_deficit.iterrows():
            res = 0

            for i in range(index, len(team_arr['team'])):

                if res < row['need'] * 0.95 and team_arr['available'][i] < row['need']:
                    res += team_arr['available'][i]
                    index += 1
                    team_list.append(team_arr['team'][i])
                    scenario_name.append(f'Scenario {s}')
                    inbox_assignment.append(row['inbox'])
                    region_assignment.append(row['region'])
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
    scenario_creator(inbox_need_deficit=inbox_need_deficit).to_csv(file, sep='\t', index=False)
exit()
