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
SELECT id, Match_Data FROM MATCH_DATA WHERE elo='diamond' LIMIT 10
'''

cursor = connection.execute(query)
# id_column = [row['id'] for row in cursor.fetchall()]
# matches = [row['Match_Data'] for row in cursor.fetchall()]
id_column=[]
matches=[]
for row in cursor.fetchall():
    id_column.append(row['id'])
    matches.append(row['Match_Data'])

matches = rf.clean_erroneous_matches(matches) # clean up 404's, 504's etc
print(len(matches))


# for match in matches:
#     count = 0
#     for participant in json.loads(match)['participants']:
#         if rf.is_adc(participant):
#             count=count+1
#     print(json.loads(match)['gameId'],f'ADCs:  {count}')

champs_dec= rf.decode_champion_ddragon(r'D:\League Analytics\Code\RIOT-API\champion.json')


#print(champs)
table_header=['Team', 'Champion', 'Lane', 'Role', 'CS/min at 10', 'ADC Score', 'Sup Score']
table_rows=[]
#I want Match ID, Team, Champion, CS10, LANE, ROLE, ADC SCORE, SUP SCORE
for match in matches:
    gameId = json.loads(match)['gameId']
    table_rows.append(['    ', '    ', '    ', f'Match: {gameId}',' ' ,' ','    ' ])
    for player in json.loads(match)['participants']:
        champ =champs_dec[str(player['championId'])]
        role = player['timeline']['role']
        lane = player['timeline']['lane']
        CS10 = player['timeline']['creepsPerMinDeltas']['0-10']
        ad_score=rf.is_adc(player)[0]
        supp_score=rf.is_supp(player)[0]
        if player['teamId'] == 100:
            team = 'Red'
        else:
            team = 'Blue'

        table_rows.append([team, champ, lane, role, CS10, ad_score, supp_score])

print(tabulate(table_rows, headers=table_header, tablefmt='orgtbl'))



#print('Score', score, 'Champion ID',player['championId'],'Role',player['timeline']['role'], 'Lane:', player['timeline']['lane'], 'CSmin10:', player['timeline']['creepsPerMinDeltas']['0-10'], 'Team:',player['teamId'])

# blue_team=[x for x in participants if x['teamId']==100]
# red_team=[x for x in participants if x['teamId']==200]
