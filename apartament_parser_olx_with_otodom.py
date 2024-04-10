from bs4 import BeautifulSoup
import datetime
import logging
import re
import requests
from rich.progress import track, Progress
from rich.console import Console
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import ast

progress = Progress()

def find_list(page_url, user_headers):
    page_responce = requests.get(page_url, headers=user_headers)
    if page_responce.status_code == 200:
        page_content = page_responce.content.decode()
        page_soup = BeautifulSoup(page_content, 'lxml')
        list_of_ads = page_soup.find_all(href=re.compile("/oferta/"))
        url_list = [link['href'] for link in list_of_ads]
        olx_list = ['https://olx.pl'+el for el in url_list if '/d/oferta' in el]
        otodom_list = [el for el in url_list if 'otodom' in el]
        return olx_list, otodom_list
    else:
        print('Request problems\n')
        print(f'{page_url} : {page_responce.status_code} {page_responce.reason}')
        return []

def scrap_ad(ad_url, user_headers, results_file):
    ad_responce = requests.get(ad_url, headers=user_headers)
    if ad_responce.status_code == 200:
        ad_content = ad_responce.content.decode()
        ad_soup = BeautifulSoup(ad_content, 'lxml')
        area = ad_soup.find('p', string=re.compile('Powierzchnia')).string          #powierzchnia
        a = ad_soup.find(string=re.compile("price")).string
        try:
            content_dict = ast.literal_eval(a)
        except:
            content_dict = {'offers':{'price':'N/A', 
                                    'areaServed':{'name':'N/A'}}}
        price = content_dict['offers']['price']                         #cena
        nbrhood = content_dict['offers']['areaServed']['name']          #dzielnica   
        b = ad_soup.find('p', string=re.compile("Liczba pokoi")).string
        match = re.search(r":(.*)", b)
        nr_rooms = match.group(1)                                              #liczba pokoi
        furn = ad_soup.find('p', string=re.compile('Umeblowane')).string           #umeblowane
        bld_type = ad_soup.find('p', string=re.compile('Rodzaj zabudowy')).string   #rodzaj zabudowy
        try:
            floor_str = ad_soup.find('p', string=re.compile('Poziom')).string               #piętro
            match = re.search(r":(.*)", floor_str)
            floor = match.group(1)
        except:
            floor = 'N/A'
        try:
            rent_str = ad_soup.find('p', string=re.compile('Czynsz')).string    #czynsz
            match = re.search(r":(.*)", rent_str)
            rent = match.group(1)
        except:
            rent = 'N/A'
        with open(results_file, "a", encoding='utf-8') as f:
            f.write("\""+nbrhood+"\",")
            f.write("\""+str(price)+"\",")
            f.write("\""+area+"\",")
            f.write("\""+nr_rooms+"\",")
            f.write("\""+furn+"\",")
            f.write("\""+bld_type+"\",")
            f.write("\""+floor+"\",")
            f.write("\""+rent+"\",")
            f.write("\""+ad_url+"\"")
            f.write("\r")
        return 

def scrap_otd(ad_url, user_headers, results_file):
    ad_responce = requests.get(ad_url, headers=user_headers)
    if ad_responce.status_code == 200:
        ad_content = ad_responce.content.decode()
        ad_soup = BeautifulSoup(ad_content, 'lxml')
        try:
            area = ad_soup.find(attrs={"data-testid": "table-value-area"}).text        #powierzchnia
        except:
            area = 'N/A'
        try:
            nr_rooms = ad_soup.find(attrs={"data-testid": "table-value-rooms_num"}).text      #liczba pokoi
        except:
            nr_rooms = 'N/A'
        try:
            rent = ad_soup.find(attrs={"data-testid": "table-value-deposit"}).text     #czynsz
        except:
            rent = 'N/A'
        try:
            floor = ad_soup.find(attrs={"data-testid": "table-value-floor"}).text  #piętro
        except:
            floor = 'N/A'
        try: 
            bld_type = ad_soup.find(attrs={"data-testid": "table-value-building_type"}).text   #rodzaj zabudowy
        except:
            bld_type = 'N/A'
        price = ad_soup.find(attrs={"aria-label": "Cena"}).text                #cena
        try:
            nbrhood = ad_soup.find_all(attrs={"class": "css-1in5nid e19r3rnf1"})[3].text    #dzielnica  
            if nbrhood == 'Warszawa':
                nbrhood = ad_soup.find_all(attrs={"class": "css-1in5nid e19r3rnf1"})[4].text       #dzielnica  
        except:
            nbrhood = 'N/A' 
        try: 
            furn = ad_soup.find(attrs={"data-testid": "table-value-constructtion_status"}).text   #umeblowane
        except:
            furn = 'N/A'                  
        with open(results_file, "a", encoding='utf-8') as f:
            f.write("\""+nbrhood+"\",")
            f.write("\""+str(price)+"\",")
            f.write("\""+area+"\",")
            f.write("\""+nr_rooms+"\",")
            f.write("\""+furn+"\",")
            f.write("\""+bld_type+"\",")
            f.write("\""+floor+"\",")
            f.write("\""+rent+"\",")
            f.write("\""+ad_url+"\"")
            f.write("\r")
        return 



def scraping_data(url, page_nr, user_headers, results_file, task_id):
    page_url = url+str(page_nr)
    olx_list = find_list(page_url, user_headers)[0]
    otodom_list = find_list(page_url, user_headers)[1]
    if olx_list:
        progress.update(task_id, total=len(olx_list))
        progress.start_task(task_id)
        for ad in olx_list:
            scrap_ad(ad, user_headers, results_file)
            progress.update(task_id, advance=1)
    if otodom_list:
        progress.update(task_id, total=len(otodom_list))
        progress.start_task(task_id)
        for ad in otodom_list:
            scrap_otd(ad, user_headers, results_file)
            progress.update(task_id, advance=1)
        
        


if __name__ == "__main__":
    now=datetime.datetime.now()
    time_now=now.strftime("%H_%M")
    results_path = f"results_{time_now}.csv"
    with open(results_path, "w", encoding='utf-8') as f:
        f.write("Neighbourhood, Price, Area, Rooms, Furniture, Building, Floor, Rent, Link")
        f.write("\r")


    url = 'https://www.olx.pl/nieruchomosci/mieszkania/wynajem/warszawa/?page='
    firefox_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'}
    chrome_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    
    now = time.time()
    with progress:
        with ThreadPoolExecutor() as pool:
            for page_nr in range(1,25):
                task = progress.add_task(f'Parsing data from page {page_nr}', start=False)
                pool.submit(scraping_data, url, page_nr, chrome_headers, results_path, task)
    
    delta = time.time()-now
    print('{:0.2f} s'.format(delta))
