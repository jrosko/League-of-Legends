import riot_functions as rf
from itertools import cycle
import sqlite3
import time
import json
from tabulate import tabulate
#Access the gold database
db_path=r'D:\League Analytics\Databases\match_data_13_09_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

query = '''
SELECT id, Match_Data FROM MATCH_DATA WHERE elo='diamond' LIMIT 200
'''

cursor = connection.execute(query)

id_column=[]
matches=[]
for row in cursor.fetchall():
    id_column.append(row['id'])
    matches.append(row['Match_Data'])

matches = rf.clean_erroneous_matches(matches) # clean up 404's, 504's etc

# Compute rito's lane assignment status
overall, bot = rf.lane_assignment_stats(matches)
print(overall)
print(bot)


# Get the championId : ChampionName map
champs_dec= rf.decode_champion_ddragon(r'D:\League Analytics\Code\RIOT-API\champion.json')

# Create table with summoner details, some stats and ADC/Support True/False scores for every match
table_header=['Team', 'Champion', 'Lane', 'Role', 'CS/min at 10', 'ADC Score', 'Sup Score']
table_rows=[]
for match in matches[0:10]:
    gameId = json.loads(match)['gameId']
    table_rows.append(['    ', '    ', '    ', f'Match: {gameId}',' ' ,' ','    ' ])
    for player in json.loads(match)['participants']:
        champ =champs_dec[str(player['championId'])]
        role = player['timeline']['role']
        lane = player['timeline']['lane']
        CS10 = player['timeline']['creepsPerMinDeltas']['0-10']
        ad_score=rf.is_adc(player)[1]
        supp_score=rf.is_supp(player)[1]
        if player['teamId'] == 100:
            team = 'Red'
        else:
            team = 'Blue'
        table_rows.append([team, champ, lane, role, CS10, ad_score, supp_score])

print(tabulate(table_rows, headers=table_header, tablefmt='orgtbl'))

#Compute my assignment statistics
bot_count_all = {}
kk=0
print(matches[58])
for match in matches:

    print(kk)
    kk=kk+1
    bot_count = 0
    for player in json.loads(match)['participants']:
        ad_score=rf.is_adc(player)[0]
        supp_score=rf.is_supp(player)[0]
        if ad_score==True or supp_score==True:
            bot_count=bot_count + 1
    if str(bot_count) in bot_count_all:
        bot_count_all[str(bot_count)] = bot_count_all[str(bot_count)] + 1
    else:
        bot_count_all[str(bot_count)] = 1

print(bot_count_all)
