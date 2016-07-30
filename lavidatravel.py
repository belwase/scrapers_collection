from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import sys
import re


class Lavidatravel(object):


    def __init__(self):
        # initializations
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.MAIN_URL = 'https://www.lavidatravel.nl'
        self.BASE_URL = 'https://www.lavidatravel.nl/vakantie/'


    def scrape_deals(self, country, limit=1):
    
        # Get the deal page
        deal_url = self.BASE_URL + country+ '?TransportType=Flight'
        resp = self.session.get(deal_url)
        soup = BeautifulSoup(resp.text)
        ADMIN_DATA = []
        
        tbl_price =soup.findAll("div", { "class" : "info" })
       
        for item in tbl_price:
            data_dict = {}
            # Scrape the required info
            title = item.find('div',{'class':'titlewrap'}).find('a').text.strip()
            link = item.find('div',{'class':'info-plus'})
            link = link.find('div',{'class':'booking-button'})
            link = self.MAIN_URL+ link.find('a')['href']
            star_rating = item.find('div',{'class':'stars'}).find('div')['class'][1][-2:-1]
            staying = item.find('div',{'class':'info-plus'})
            #staying = (staying.find('div',{'class':'price-info'}).findAll('span')[2].text)
            staying = (staying.find('div',{'class':'price-info'}).find(text=re.compile(r'dagen')))
            date = item.find('div',{'class':'info-plus'})
            date = date.find('div',{'class':'price-info'}).findAll('span')[1].text
            price = item.find('div',{'class':'info-plus'})
            price = price.find('div',{'class':'price'}).find('span',{'class':'euro'}).text.strip()
            price = price.split(',-')[0].encode('ascii', 'ignore').strip()
            price = price.replace('.', '').replace(',', '.')
            departing = item.find('div',{'class':'info-plus'})
            departing = departing.find('span', {'class': 'departure-airport'})
            if departing:
                departing = departing.text
            else:
                departing = ''
            # Package into a dictionary
            if staying.strip():
                staying = staying[0]
            else:
                staying = None
            data_dict = {'title': title,
                        'deeplink': link,
                        'stars': star_rating,
                        'country': country,
                        'days_of_staying': staying,
                        'date': date,
                        'departing': departing,
                        'price': int(price)
            }
            ADMIN_DATA.append(data_dict)

        return ADMIN_DATA
        
        
def execute(country):

        scraper = Lavidatravel()
        data = []
        deal = scraper.scrape_deals(country)
        #print deal
        for item in deal:
            #print item
            fmdate = datetime.strptime(item['date'], '%d-%m-%Y')
            d = {
                    'title': item['title'],
                    'deeplink': item['deeplink'],
                    'stars': item['stars'],
                    'date': fmdate,
                    'price': item['price'],
                    'persons': 2,
                    'country': item['country'],
                    'departure_from': item['departing'],
                    'days_of_staying': item['days_of_staying']
            }
            data.append(d)
            #print d
        return data


"""
def execute():
#if __name__ == '__main__':
    lt = Lavidatravel();
    # countries = {'bulgarije':'250','curacao':'500','cyprus':'300','egypte':'250','gambia':'550','griekenland':'199',
                #'macedonie':'199','portugal':'250','spanje':'250','tunesie':'300','turkije':'200'
                #}
    # country = arke.get_list_of_all_countries()
    response = lt.scrape_deals('aruba')
    return response
"""

#execute('bulgarije')
