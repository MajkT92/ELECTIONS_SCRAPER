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

def get_result_links(start_url, base_url):
    response = requests.get(start_url)

    # Správné formátování
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a', href=True)
    result_links = []

    for link in links:
        if 'ps311' in link['href']:
            code = link['href'].split('=')[-1]
            obec_info = link.find_next('td').get_text(strip=True)

            obec_nazev = ' '.join(word for word in obec_info.split() if not word.isdigit())
            result_links.append((obec_nazev, base_url + link['href'], code))

    return result_links