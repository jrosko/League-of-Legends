import riot_functions as rf
from itertools import cycle
import sqlite3
import json
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt

# Investigating the conncection between winrate and anti healing items when the enemy team has the sole healer in the game

db_path=r'D:\League Analytics\Databases\match_data_13_09_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

query = '''
SELECT Match_Data FROM MATCH_DATA WHERE elo='silver'
'''
cursor = connection.execute(query)

matches=[]
for row in cursor.fetchall():
    matches.append(row['Match_Data'])
matches = rf.clean_erroneous_matches(matches) # clean up 404's, 504's etc
# Let's Identify games where one side has Raka/Yummi/Nami/Senna and the other doesn't
botlanes={}

for match in matches:
    #First we find AD/SUP pairs
    game_output = {}
    game = json.loads(match)
    gameId = game ['gameId']
    players  = game['participants']
    target_players = set(['Blue_ADC', 'Blue_SUP', 'Red_ADC', 'Red_SUP'])
    for player in players:
        if player['teamId']==100:
            team='Red'
        else:
            team='Blue'
        if rf.is_adc(player)[0]==True:
            play_descr = team + '_ADC'
            if play_descr not in game_output:
                game_output[play_descr] = [player['participantId'], player['championId']]
            else:
                game_output['double_player'] = ['double_player']
        elif rf.is_supp(player)[0]==True:
            play_descr = team + '_SUP'
            if play_descr not in game_output:
                game_output[play_descr] = [player['participantId'], player['championId']]
            else:
                game_output['double_player'] = ['double_player']
    found_players = set(game_output.keys())
    if len(target_players.difference(found_players))==0 and 'double_player' not in game_output: # care when editing, non commutativeness
        botlanes[str(gameId)]=game_output

# Get the championId : ChampionName map
champs_dec= rf.decode_champion_ddragon(r'D:\League Analytics\Code\RIOT-API\champion.json') # this is of the form id:name
 # Want to cast this into healers = {name : id}
healers ={}
for key in champs_dec:
    if champs_dec[key] in ['Soraka', 'Nami', 'Sona', 'Yummi', 'Senna']:
        healers[champs_dec[key]] = key
healers = set([int(n) for n in healers.values()]) # just champ id's


opposing_adcs = {}
for match_id in botlanes:
    if match_id!=4809566181: # some shifty match, investigate
    # Data is of the form { match_id: [ Red_ADC : [ participant id, champion id], [],], match_id: [...] ]}
        current_botlane = botlanes[match_id]
        just_champions = set([inner_list[1] for inner_list in botlanes[match_id].values()])
        if len(healers.intersection(just_champions))==1: #just one healer out of 4 Botlaners
            healer = list(healers.intersection(just_champions))[0]
            for member in current_botlane:
                if healer in current_botlane[member]:
                    healer_champ = current_botlane[member][1]
                    healer_participantId = current_botlane[member][0]
                    healer_team = member[:-4]
                    adcs = ['Blue_ADC', 'Red_ADC']
                    current_adc = healer_team + '_ADC'
                    adcs.remove(current_adc)
                    enemy_adc = adcs[0]
                    enemy_adc = current_botlane[enemy_adc]
                    # I want match id : participant id for enemy adc
                    opposing_adcs[match_id]= enemy_adc[0]

# Now I have a list of ADC participant and match ID's for ADC's opposing a healer support
# What I want next is whether they won or not and whether they had executioners or not


executioner_adcs = {}
for match_id in opposing_adcs:
    for match in matches:
        game = json.loads(match)
        if int(match_id) == game['gameId']:
            for participant in game['participants']:
                if participant['stats']['participantId'] == opposing_adcs[match_id]:
                    win = participant['stats']['win']
                    items = list(rf.grab_items(participant['stats']))
                    if 3033 in items or 3123 in items:
                        executioners=True
                    else:
                        executioners=False
                    executioner_adcs[match_id] = [win, executioners]



games_without = 0
wins_without =0
games_with = 0
wins_with = 0

for match_id in executioner_adcs:
    if executioner_adcs[match_id][1]==False:
        games_without=games_without + 1
        if executioner_adcs[match_id][0]==True:
            wins_without = wins_without + 1
    if executioner_adcs[match_id][1]==True:
        games_with = games_with + 1
        if executioner_adcs[match_id][0]==True:
            wins_with = wins_with + 1

print(games_with)
print(games_without)
print(len(executioner_adcs))

print(wins_with/games_with)
print(wins_without/games_without)
