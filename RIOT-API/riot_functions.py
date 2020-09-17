import json
import requests
import time
import urllib.parse


def sum_details_from_name(summonerName, api_key):
    """ Returns a python dictionary with keys including accountId, id (summoner id), summonerLevel,
    name (summoner name). Others are puuid, revisionDate, profileIconId - look at rito's docs for these.
    """
    target_url=f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}'
    response=requests.get(target_url, headers={'X-Riot-Token': api_key})
    return response.status_code, response.json()


def get_ranked_games(account_id,api_key, queue, limit): #soloq = 420
    """ Returns a list of the format [[gameId, account id, champion, role, lane, timestamp, season],[game..],..]
    """
    target_url=f'https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/{account_id}'
    response=requests.get(target_url, headers={'X-Riot-Token': api_key}, params={'queue':queue, 'endIndex' : limit})
    result = []
    if 'matches' in response.json():
        for item in response.json()['matches']:
            result.append([item['gameId'] ,account_id, item['champion'], item['role'], item['lane'], item['timestamp'], item['season']])
    return response.status_code, result

def get_match_data(matchId, api_key):
    target_url=f'https://euw1.api.riotgames.com/lol/match/v4/matches/{matchId}'
    response=requests.get(target_url, headers={'X-Riot-Token': api_key})
    return response.status_code, response.json()

def sample_summoners(seed_summoner, iterations, api_key):
    ''' Sample summoners by going through the seed's most recent match, then the most recent match of those 9.. etc
    for a number of iterations. I will at some point add some kind of progress indicator '''
    status, _  = sum_details_from_name(seed_summoner, api_key)
    time.sleep(1.3)
    if status!=200:
        print(f'Error in sample_summoners, seed_summoner: {seed_summoner}, Error {status}')
    else:
        seed_id = _['accountId']
        accounts=[[seed_id]] # I am building a list of lists [[first acc], [following 9], [following 72]]
        # Expanding the accounts list as new iterations are finished, and using the result for the further iteration
        for n in range(0, iterations):
            print(f'Sampling iteration {n} underway')
            accs=[] # temp list to house the accounts of the current iteration
            for account in accounts[n]:
                status, ranked_games = get_ranked_games(account,api_key, 420, 1)
                time.sleep(1.3)
                if status==200:
                    match_id = ranked_games[0][0] # [0][0] is the game id of the first game, also if something goes wrong with the request, ranked will be 0
                    status_2, accIds_ = accIds_from_match(match_id, seed_id, api_key)
                    time.sleep(1.3)
                    if status_2==200:
                        accs = accs +  accIds_
                    else:
                        print(f'Error when getting account ids from match_id {match_id}, Error {status_2}')
                else:
                    print(f'Error in sample_summoners when getting most recent ranked game for account: {account}, status: {status}, skipping')
            accounts.append(accs) # Add the accs list to accounts, and reinitialise it to =[] for the next iteration
    return accounts

def accIds_from_match(match, seed_summoner, api_key):
    """If seed_summoner is 0, returns all match participants,
    if seed_summoner is given, returns the other 9
    """
    status, matchdata = get_match_data(match, api_key) #status not used here but left for later when I sort out exceptions
    if status!=200:
        print(f'Error in accIds_from_match, match {match}, status {status}')
        return status, 0
    else:
        accounts=[]
        for k in range(0,10):
            acc_id = matchdata['participantIdentities'][k]['player']['accountId']
            if acc_id != seed_summoner:
                accounts.append(acc_id)
        return status, accounts

def lane_assignment_stats(match_list):
    """takes a list of strings containing match data, finds lane assignment (by rito).
    Returns number of times each lane was found per match in match_list, and stats on how many botlaners got found each match """
    lanes = ['TOP', 'BOTTOM', 'MIDDLE', 'JUNGLE']
    counts = {'TOP':0, 'BOTTOM':0, 'MIDDLE':0, 'JUNGLE':0} # Total counts in whole match dataset that I will later divide by number of matches
    bot_counts={} # Counting how many games have at least 1,2,3,4 botlaners identified, will also normalise before outputting
    for match in match_list:
            counter_2 = 0 # Another counter that isnt total count but only for this match
            for player in json.loads(match)['participants']:
                assigned_lane = player['timeline']['lane']
                if assigned_lane == 'BOTTOM':
                    counter_2 = counter_2 + 1
                if assigned_lane in lanes:
                    counts[assigned_lane]=counts[assigned_lane]+1
            if str(counter_2) in bot_counts:
                bot_counts[str(counter_2)] = bot_counts[str(counter_2)] + 1
            else:
                bot_counts[str(counter_2)] = 1
    for lane in lanes:
            counts[lane]=counts[lane]/(2*len(match_list))
    # Returns
    return counts, bot_counts

def grab_items(participant_stats):
    """ get a list of items bought by the player from player['stats']"""
    itemlist = [participant_stats['item0'], participant_stats['item1'],participant_stats['item2'],participant_stats['item3'],participant_stats['item4'],participant_stats['item5'],participant_stats['item6']]
    return set(itemlist)


def decode_champion_ddragon(filepath):
    # Open the data dragon file from rito with all the champions
    # Cast the file in a more readable form so I dont have to open and sort it every time I wanna go from champ Id to champ name
    with open(filepath,  encoding='utf8') as json_file:
        data = json.load(json_file)
    output = {}
    for name in data['data']:  # is of form {name1 : { 'key': name1, 'id': number1}, name2 : { 'key': number2, 'id': name2}}
        number = data['data'][name]['key']
        c_name = data['data'][name]['id']
        output[number] = c_name
    return output


def is_supp(player):
    """Scoring if a player is likely to be the support, for use in finding botlaners
    Returns True/False + Score (I will get rid of score once function works well)"""
    with open(r'D:\League Analytics\Code\RIOT-API\bot_champions.txt') as json_file:
        bot_champs = json.load(json_file)
    support_items = set([3850, 3851, 3853, 3854, 3855, 3857, 3858, 3859, 3860, 3862, 3863, 3864])
    items = grab_items(player['stats'])
    score = 0
    if player['timeline']['role'] == 'DUO_SUPPORT':
        score = score + 0.5
    if len(items.intersection(support_items)) > 0:
        score = score + 3
    if player['timeline']['creepsPerMinDeltas']['0-10'] <=3:
        score = score + 1
    if player['spell1Id'] !=11 and player['spell2Id'] !=11:
        spells = set([player['spell1Id'],player['spell2Id']])
        exhaust_ignite = set([3,14])
        if len(spells.intersection(exhaust_ignite))>0:
            score = score + 0.5
    if player['championId'] in bot_champs['SUPP'].values():
        score = score + 1
    if score>=4:
        return True, score
    else:
        return False, score


def is_adc(player):
    """ Scoring if the player is an ADC, for use in finding botlaners
    Returns True/False + Score (I will get rid of score once function works well)"""
    with open(r'D:\League Analytics\Code\RIOT-API\bot_champions.txt') as json_file:
        bot_champs = json.load(json_file)
    score = 0
    items = grab_items(player['stats'])
    if player['timeline']['creepsPerMinDeltas']['0-10'] > 3.5:
        score = score + 1
    if player['championId'] in bot_champs['ADC'].values():
        score = score + 1
    if is_supp(player) == False:
        score = score + 1
    if player['timeline']['role'] == 'DUO_CARRY':
        score = score + 1
    spells = set([player['spell1Id'],player['spell2Id']])
    heal_cleanse_exhaust = set([1,7,3])
    if len(spells.intersection(heal_cleanse_exhaust))>0:
        if 11 not in spells:
            score = score + 1
    if player['timeline']['lane']=='MIDDLE' or player['timeline']['lane']=='TOP':
        score = score + - 1
    else:
        if 11 not in spells:
            score = score + 1
    if score>=4:
        return True, score
    else:
        return False, score

# I need to clean up the matches list because there are some entries that are just 503 or 504 errors
# These have no usual keys, but do have match['status']['status_code']
def clean_erroneous_matches(matches):
    """ Takes a list of match data (string), json's it, removes status codes !=200
    Also some matches have no cs scores, throwing out too """
    matches = matches
    n_s=[]
    for n in range(0, len(matches)):
        match=json.loads(matches[n])
        if 'participants' not in match:
            if match['status']['status_code']!=200:
                n_s.append(n)
        elif match['gameDuration'] < 300: # less than 5min, probably remake, will have cs scores Missing
            n_s.append(n)
    n_s.reverse()
    for m in n_s:
        matches.pop(m)
    return matches


#
# def get_botlaners(match_list):
#     """takes a match list, finds blue and red botlaners"""
#     result={} # output
#     support_items = set([3850, 3851, 3853, 3854, 3855, 3857, 3858, 3859, 3860, 3862, 3863, 3864])
#     #summoner spells
#     sums = {'Flash':4, 'Ignite':14, 'Heal':7, 'Exhaust':3, 'Smite':11, 'Cleanse':1}
#     with open(r'D:\League Analytics\RIOT-API\bot_champions.txt') as json_file:
#         bot_champs = json.load(json_file)
#     for match in match_list:
#         players = json.loads(match)['participants'] #Load only participant stats
#         #Count botlaners - using this as sort of a threshold, won't try to assign games with more than 2 orphan laners, for now
#         botlane_count=0
#         for player in players:
#             if player['timeline']['lane']=='BOTTOM':
#                 botlane_count = botlane_count + 1
#         # Apply the "threshold"
#         if botlane_count>=2:
#             expected_laners = ['100_ADC', '100_SUPP', '200_ADC', '200_SUPP'] #bookkeeping
#             laners=[]
#             for player in players:
#                 str_teamid = str(player['teamId'])
#                 # Two common options are that lane is correctly assigned or un-assigned, yet the 'role' is correct
#                 if player['timeline']['lane']=='BOTTOM' or player['timeline']['lane']=='NONE':
#                     if player['timeline']['role'] == 'DUO_CARRY':
#                         laners.append([player['teamId'], 'ADC', player['participantId']])
#                         expected_laners.remove(str_teamid+'_'+'ADC')
#                     elif player['timeline']['role'] == 'DUO_SUPPORT':
#                         if
#                         laners.append([player['teamId'], 'SUPP',player['participantId']])
#                         expected_laners.remove(str_teamid+'_'+'SUPP')
#                 elif player['timeline']['role'] == 'SOLO': # 'SOLO' laner
#                     items = grab_items(player['stats'])
#                     if len(items.intersection(support_items)) > 0: # has support items
#                         if player['timeline']['creepsPerMinDeltas']['0-10'] < 3: # laning phase farm
#                             if player['championId'] in bot_champs['SUPP'].values(): # plays a support champ in a broader sense of the meta
#                                 laners.append([str_teamid, 'SUPP',player['participantId']])
#                                 expected_laners.remove(str_teamid+'_'+'SUPP')
#                     elif len(items.intersection(support_items)) ==0:
#                         # doesnt have smite, also rule out smite for supp,
#                         # provision for the player's lane to actually be assigned bottom here too
#                         # if it isnt, then look further
#                         if player['timeline']['creepsPerMinDeltas']['0-10'] > 3:
#                             if player['championId'] in bot_champs['ADC'].values():
#                                 laners.append([str_teamid, 'ADC',player['participantId']])
#                                 expected_laners.remove(str_teamid+'_'+'ADC')
#
#
#                     elif
#                         else:
#                             laners.append([player['teamId'], 'ADC',player['participantId']])
#                             expected_laners.remove(str_teamid+'_'+'ADC')
#                         # HERE ADD ALSO THOSE WHO ARE LANE NONE BUT ROLE DUO_SUP, DUO_CAR
#                     elif player['timeline']['lane']=='NONE':
#
#             # BELOW MIGHT BECOME REDUNDANT
#             if botlane_count==3:
#                 #Missing laner should be last remaining in expected_laners
#                 if expected_laners[0][4:]=='SUPP':
#                     exp_team_id = expected_laners[0][0:3]
#                     for player in players:
#                         str_teamid = str(player['teamId'])
#                         if str_teamid == exp_team_id:
#                             items = grab_items(player['stats'])
#                             if len(items.intersection(support_items)) > 0:
#                                 laners.append([str_teamid, 'SUPP',player['participantId']])
#                 if expected_laners[0][4:]='ADC':
#                     exp_team_id = expected_laners[0][0:3]
#                     for player in players:
#                         str_teamid = str(player['teamId'])
#                         if str_teamid == exp_team_id:
#                             #grab champion_id
#                             # i will need dict.values()
#
#
#
#             # add
#             if botlane_count==2:
#
#
#         gameId=json.loads(match)['gameId']
#         if len(laners)==4:
#             result[gameId]=laners
#     return result
