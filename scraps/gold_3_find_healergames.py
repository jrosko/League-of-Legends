import sqlite3
import json
import time
import riot_functions as rf

#Here goes the api key
api_key=''

#Access the gold database
db_path=r'D:\League Analytics\Databases\league_gold_14_06_2020.db'
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

query = """SELECT gameId from RIOT_GOLD_3_MATCHES
        WHERE
        (champion=350 OR champion = 235 OR champion = 37 OR champion =267)
        AND
        timestamp> 1589068800000
        """
cursor = connection.execute(query)
games = [row['gameId'] for row in cursor.fetchall()]

cursor.close()

#Timestamp in milliseconds: 1589068800000
#Date and time (GMT): Sunday, 10 May 2020 00:00:00
#http://ddragon.leagueoflegends.com/cdn/10.12.1/data/en_US/champion.json
# Yummi is 350, Senna is 235, sona is 37, raka is 16, nami is 267, ww is 19
