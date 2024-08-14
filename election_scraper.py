"""
election_scraper.py: třetí projekt do Engeto Online Python Akademie
author: Michal Toman
email: mtoman92@gmail.com
discord: majk923278
"""

import requests
from bs4 import BeautifulSoup
import csv
import argparse

def fetch_data_from_result_page(result_url, obec, code):
    response = requests.get(result_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #Data tabulky
    rows = soup.find_all('tr')
    data = {'code': code, 'location': obec}

    #Registrovaní voliči (registered)
    registered = soup.find('td', headers='sa2')
    if registered:
        data['registered'] = registered.get_text(strip=True)

    #Počet vydaných obálek (enveloped)
    enveloped = soup.find('td', headers='sa3')
    if enveloped:
        data['enveloped'] = enveloped.get_text(strip=True)

    #Počet platných hlasů (valid)
    valid_tag = soup.find('td', headers='sa6')
    if (valid_tag):
        data['valid'] = valid_tag.get_text(strip=True)

    for row in rows:
        strana_tag = row.find('td', class_='overflow_name')
        hlasy_tag = row.find_all('td', class_='cislo')

        if strana_tag and len(hlasy_tag) > 0:
            nazev_strany = strana_tag.get_text(strip=True)
            platne_hlasy = hlasy_tag[-1].get_text(strip=True)
            data[nazev_strany] = platne_hlasy

    return data