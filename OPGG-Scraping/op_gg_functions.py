import math
from selenium import webdriver
from bs4 import BeautifulSoup
import random
import re
import time


def which_page(number):
    """Find out on which page of op.gg is the rank: number """
    page, remainder = divmod(number - 1, 100)
    return str(page+1)

def sample(initial_rnk, final_rnk, number):
    """
    Pseudorandom sample of N=number of integers between initial_rnk and final_rnk.
    Returns a dictionary of structure  'page' : [rank1, rank2....]

    """
    #ranks=[randint(initial_rnk, final_rnk) for _ in range(number)]
    ranks = random.sample(range(initial_rnk, final_rnk), number)
    result = {}
    for rank in ranks:
        page = which_page(rank)
        if page in result:
            result[page].append(rank)
        else:
            result[page] = [rank]
    return result

def get_summoner_soup(page_rank_dict):
    """
    Connect to op.gg and look up pages specified by "page" and collected summoner names
    from the ranks specified under the page key of the input dict.
    Returns a list of the form [name, op.gg rank]
    """
    driver = webdriver.Firefox(executable_path=r'C:\Users\elpresidente_2\AppData\Local\Programs\Python\Python38-32\geckodriver\geckodriver.exe')
    result = []
    k = 0
    for page in page_rank_dict:
        k = k + 1
        if k%10==0:
            print(f'Processing page {str(k)} out of {str(len(page_rank_dict))}')
        driver.get(f"https://euw.op.gg/ranking/ladder/page={page}")
        content = driver.page_source
        soup = BeautifulSoup(content,features="html.parser")
        content = soup.find_all('tr', class_='ranking-table__row')
        for row in content:
            ladder_rank_match = re.search('e__cell--rank">.+</td><td class="sel',str(row))
            ladder_rank = ladder_rank_match.group()[15:-19]
            if int(ladder_rank) in page_rank_dict[page]:
                summoner_match=re.search('userName=.+"><img',str(row))
                summoner_name = summoner_match.group()[9:-6]
                result.append([summoner_name, ladder_rank])
        time.sleep(1.5)
    driver.quit()
    return result
