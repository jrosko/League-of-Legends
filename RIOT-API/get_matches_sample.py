import riot_functions as rf
from itertools import cycle
import sqlite3
import time
import json

'''Getting summoners the most recent game of "seed summoner",
and then the players from their most recent game.. etc
for a given number of iterations specified in sample_summoners()
 '''
#
# # Let's get some dia/silver summoners and load the api_key
parameters = r'D:\RIOT_API\parameters.txt'
params = [line.rstrip('\n') for line in open(parameters)] #API KEY, Diamond Summoner, Silver Summoner

elo_fnames = cycle(['Diamond_Accounts.txt','Silver_Accounts.txt'])
print(params[1:])
for name in params[1:]:
    print(f'Sampling summoners from {name}')
    summoners = rf.sample_summoners(name, 3, params[0]) # The '3' is the number of iterations to dig through
    flattened_sums = [sumo for iteration in summoners for sumo in iteration]
    with open(next(elo_fnames), 'w') as f:
        for account in flattened_sums:
            f.write(account+'\n')
    f.close()


silvers = [line.rstrip('\n') for line in open('Silver_Accounts.txt')]
diamonds = [line.rstrip('\n') for line in open('Diamond_Accounts.txt')]

#open a Database
db_path=r'D:\League Analytics\Databases\match_data_13_09_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# trololo
#Create a table to house the results
query= 'CREATE TABLE MATCH_DATA (id INTEGER PRIMARY KEY, Match_Data VARCHAR NOT NULL, elo VARCHAR NOT NULL, Date VARCHAR NOT NULL)'
cursor = connection.execute(query)
elo_names = cycle(['silver','diamond'])


for elo in [silvers,diamonds]:
    n = 0 # 'progress' bar
    current_elo = next(elo_names)
    print(f'processing elo: {current_elo}')
    for account in elo:
        if n%20==0:
            print(f'processing account {n}')
        n=n+1
        status, match_list = rf.get_ranked_games(account,params[0],420,5)
        time.sleep(1.5)
        if status==200:
            for match in match_list:
                status_2, data = rf.get_match_data(match[0], params[0]) #match[0] is the match id
                time.sleep(1.5)
                if status!=200:
                    print(f'Error getting match data for match {match[0]}, status {status_2}')
                else:
                    if match[5]> 1597449600000: #match[5] is the timestamp, 15 aug
                        cursor = connection.execute('INSERT INTO MATCH_DATA VALUES(?,?,?,?)', (None, json.dumps(data,indent=4), current_elo, '13-09-2020'))
                    else:
                        pass
        else:
            print(f'Couldnt get matchlist for account {account}, status {status}')

connection.commit()
cursor.close()
