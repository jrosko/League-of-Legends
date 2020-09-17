import sqlite3
import op_gg_functions as opgg

#Create database to house the op.gg ranks and summoner names
db_path=r'D:\League Analytics\Databases\opgg_samples_17_07_2020-B3.db'
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Generate a pseudorandom samples of op.gg rankings for G3
samples = {}
samples['G3'] = opgg.sample(575198, 772384, 2000)

# Find the summoner names on op.gg given the sampling
# Save op.gg rank, summoner name pairs into the table

for rank in samples:
    summoners = opgg.get_summoner_soup(samples[rank])
    print(len(summoners))
    cursor.execute(f'CREATE TABLE OPGG_{rank}_SUMMONERS (id INTEGER PRIMARY KEY, opgg_rank INTEGER NOT NULL, summoner_name VARCHAR NOT NULL)')
    for i in range(0, len(summoners)):
        cursor.execute(f'INSERT INTO OPGG_{rank}_SUMMONERS VALUES(?,?,?)', (None, summoners[i][1],summoners[i][0]))
    connection.commit()

cursor.close()
