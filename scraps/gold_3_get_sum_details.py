import sqlite3
import urllib.parse
import json
import time
import riot_functions as rf

#Here goes the api key
api_key='RGAPI-b3ecb956-e8db-45ab-9fba-d5e252f97387'

#Access the gold database
db_path=r'D:\League Analytics\Databases\league_gold_14_06_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

#Get summoner names from the database created in op-gg-scraping/get_gold_3_sample.py
cursor = connection.execute('SELECT summoner_name from OPGG_GOLD_3_SUMMONERS')
names = [row['summoner_name'] for row in cursor.fetchall()]

#Table to host summoner names looked up on rito's API, and the resulting account id, summoner id, and player level
cursor.execute('CREATE TABLE RIOT_GOLD_3_SUMMONERS (id INTEGER PRIMARY KEY, summoner_name VARCHAR NOT NULL, accountId VARCHAR NOT NULL, summoner_id VARCHAR NOT NULL, summonerLevel INTEGER NOT NULL)')

#I am making the erroneous_codes list, shape:  "status code, summoner name". op.gg isnt 100% up to date and some names will have changed
erroneous_codes=[]

#The actual API query to get summoner names/details
for summoner in names:
    # the summoner names are extracted from url encoded link element, %XX characters need to be utf-ed
    name_decoded=urllib.parse.unquote_plus(summoner, encoding='utf-8', errors='strict')
    status_code, sum_details=rf.sum_details_from_name(name_decoded, api_key)
    if status_code==200:
        cursor.execute('INSERT INTO RIOT_GOLD_3_SUMMONERS VALUES(?,?,?,?,?)', (None, sum_details['name'],sum_details['accountId'],sum_details['id'], sum_details['summonerLevel']))
    else:
        erroneous_codes.append([status_code, name_decoded])
    time.sleep(2)
    if k%100==0: # I want to know where I am
        print(f'Summoner number {str(k)} has been processed')
    k=k+1

    # Also, note for myself, printing name_decoded in the console doesn't print the funky characters
    # but replaces them with ?. Saving name_decoded to a utf encoded file works though. So does
    # passing the name_decoded into rito api

connection.commit()
cursor.close()

with open('gold_3_erroneous.txt', 'w', encoding='utf-8') as f:
    for entry in erroneous_codes:
        string = str(entry[0]) + '\t' + entry[1] + '\n'
        f.write(string)
