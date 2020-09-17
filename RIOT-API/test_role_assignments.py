import riot_functions as rf
from itertools import cycle
import sqlite3
import time
import json
#Access the gold database
db_path=r'D:\League Analytics\Databases\match_data_13_09_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

query = '''
SELECT id, Match_Data FROM MATCH_DATA WHERE elo='diamond' LIMIT 3
'''

cursor = connection.execute(query)
# id_column = [row['id'] for row in cursor.fetchall()]
# matches = [row['Match_Data'] for row in cursor.fetchall()]
id_column=[]
matches=[]
for row in cursor.fetchall():
    id_column.append(row['id'])
    matches.append(row['Match_Data'])

# clean clean_erroneous_matches(matches)


for match in matches:
    count = 0
    for participant in json.loads(match)['participants']:
        if rf.is_adc(participant):
            count=count+1
    print(json.loads(match)['gameId'],f'ADCs:  {count}')

champs= rf.decode_champion_ddragon(r'D:\League Analytics\RIOT-API\champion.json')
print(champs)

# blue_team=[x for x in participants if x['teamId']==100]
# red_team=[x for x in participants if x['teamId']==200]
