import sqlite3
import json
import time
import riot_functions as rf

api_key = ''

#Access the gold database
db_path=r'D:\League Analytics\Databases\league_gold_14_06_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

#Get summoner names from the database created in op-gg-scraping/get_gold_3_sample.py
cursor = connection.execute('SELECT accountId from RIOT_GOLD_3_SUMMONERS')
accounts = [row['accountId'] for row in cursor.fetchall()]

#Create a table to host matches
query = """
CREATE TABLE RIOT_GOLD_3_MATCHES (
    id INTEGER PRIMARY KEY,
    gameId VARCHAR NOT NULL,
    accountId VARCHAR NOT NULL,
    champion INTEGER NOT NULL,
    role VARCHAR NOT NULL,
    lane VARCHAR NOT NULL,
    timestamp INTEGER NOT NULL,
    season INTEGER NOT NULL)
"""
cursor.execute(query)

k=0
for account_id in accounts:
    time.sleep(2)
    games = rf.get_ranked_games(account_id,api_key, 420)
    if games!=0:
        for game in games:
            gameId = game[0]
            account_id = game[1]
            champion = game[2]
            role = game[3]
            lane = game[4]
            timestamp = game[5]
            season = game[6]
            cursor.execute('INSERT INTO RIOT_GOLD_3_MATCHES VALUES(?,?,?,?,?,?,?,?)',(None, gameId, account_id, champion, role, lane, timestamp,season))
    if k%100==0: # I want to know where I am
        print(f'Account number {str(k)} has been processed')
    k=k+1

connection.commit()
cursor.close()
