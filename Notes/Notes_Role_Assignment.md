# League of Legends
 
The data I got from the API doesn't have roles/lanes assigned well, and I would like to do some stats on only botlanes, so I'm trying out some simple functions meant to fill in the data gaps by estimating who should be the botlaner.

using scoring functions: is_adc(player) and is_supp(player) from riot_functions.py
Tests carried within test_role_assignments.py

For the first 10 matches of the diamond elo sample I generated tables like this one:
9/10 correctly scored ADC/SUPP. One had a missing ADC, and upon inspection that ADC was yone so I will let that one pass.
For now, until I improve scoring functions, I am happy just developing my analysis on more "meta" matchups

| Team   | Champion    | Lane   | Role              | CS/min at 10        | ADC Score   | Sup Score   |
|--------|-------------|--------|-------------------|---------------------|-------------|-------------|
|        |             |        | Match: 4802704432 |                     |             |             |
| Red    | MissFortune | BOTTOM | DUO_CARRY         | 7.8                 | True        | False       |
| Red    | Warwick     | JUNGLE | NONE              | 0.4                 | False       | False       |
| Red    | Lux         | BOTTOM | DUO_SUPPORT       | 0.1                 | False       | True        |
| Red    | Kassadin    | MIDDLE | SOLO              | 6.8                 | False       | False       |
| Red    | Akali       | TOP    | SOLO              | 5.9                 | False       | False       |
| Blue   | Sion        | TOP    | SOLO              | 5.4                 | False       | False       |
| Blue   | Ashe        | BOTTOM | DUO_CARRY         | 7.800000000000001   | True        | False       |
| Blue   | Kindred     | JUNGLE | NONE              | 0                   | False       | False       |
| Blue   | Syndra      | MIDDLE | SOLO              | 7.6                 | False       | False       |
| Blue   | Leona       | BOTTOM | DUO_SUPPORT       | 1.1                 | False       | True        |



![Alt text](relative/path/to/img.jpg?raw=true "Title")
