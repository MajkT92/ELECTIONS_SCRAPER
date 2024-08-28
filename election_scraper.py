import requests
from bs4 import BeautifulSoup
import csv
import argparse
from urllib.parse import urljoin, urlparse

def fetch_data_from_result_page(result_url, obec, code):
    response = requests.get(result_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Data tabulky
    rows = soup.find_all('tr')
    data = {'code': code, 'location': obec}

    # Registrovaní voliči (registered)
    registered = soup.find('td', headers='sa2')
    if registered:
        data['registered'] = registered.get_text(strip=True)

    # Počet vydaných obálek (enveloped)
    enveloped = soup.find('td', headers='sa3')
    if enveloped:
        data['enveloped'] = enveloped.get_text(strip=True)

    # Počet platných hlasů (valid)
    valid_tag = soup.find('td', headers='sa6')
    if valid_tag:
        data['valid'] = valid_tag.get_text(strip=True)

    for row in rows:
        strana_tag = row.find('td', class_='overflow_name')
        hlasy_tag = row.find_all('td', class_='cislo')

        if strana_tag and len(hlasy_tag) > 0:
            nazev_strany = strana_tag.get_text(strip=True)
            platne_hlasy = hlasy_tag[-1].get_text(strip=True)
            data[nazev_strany] = platne_hlasy

    return data

def get_result_links(result_link):
    response = requests.get(result_link)

    # Správné formátování
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    links = soup.find_all('a', href=True)
    result_links = []

    for link in links:
        if 'ps311' in link['href']:
            #kod obce
            code = link.get_text(strip=True)

            obec_info_td_link = link.find_next('td')

            #td tag / ošetření None
            if obec_info_td_link is not None:
                obec_info = obec_info_td_link.get_text(strip=True)
            else:
                obec_info = None

            #ošetření v případě, že by se vyskytlo None
            obec_nazev = ' '.join(word for word in (obec_info or '').split() if not word.isdigit())

            #Celý odkaz jak z ps32 tak i z ps311
            full_link = urljoin(result_link, link['href'])

            result_links.append((obec_nazev, full_link, code))

    return result_links

def fetch_all_data(result_links):
    print("Začínám stahovat data.")
    all_data = []

    # Set pro uchování již zpracovaných odkazů
    visited_links = set()
    print('Ještě chvíli strpení....')
    for obec, result_link, code in result_links:

        # Duplicitní názvy obcí a obce začínací "X"
        if obec != 'X' and result_link not in visited_links:
            data = fetch_data_from_result_page(result_link, obec, code)
            all_data.append(data)
            visited_links.add(result_link)

    return all_data

def write_to_csv(all_data, filename):
    # Získáme všechny názvy politických stran
    all_strany = set()
    for data in all_data:
        all_strany.update(data.keys())
    all_strany.discard('code')
    all_strany.discard('location')
    all_strany.discard('registered')
    all_strany.discard('enveloped')
    all_strany.discard('valid')
    all_strany = sorted(all_strany)

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Hlavička
        header = ['code', 'location', 'registered', 'enveloped', 'valid'] + all_strany
        writer.writerow(header)

        # Samotné data
        for data in all_data:
            row = [data.get('code'), data.get('location'), data.get('registered', ''),
                   data.get('enveloped', ''), data.get('valid', '')] + [data.get(strana, '')
                    for strana in all_strany]
            writer.writerow(row)

    print(f"Data byla stažena a uložena do souboru: {filename}")

def election_scraper(base_url, output_file):
    result_links = get_result_links(base_url)
    all_data = fetch_all_data(result_links)
    write_to_csv(all_data, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and save election results.')
    parser.add_argument('base_url', type=str, help='Base URL for the election results')
    parser.add_argument('output_file', type=str, help='Output CSV file name')

    args = parser.parse_args()

    election_scraper(args.base_url, args.output_file)
