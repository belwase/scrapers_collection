from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import sys
import re


class Vakantie(object):

        MONTHS = {
            'januari': 'Jan',
            'februari': 'Feb',
            'maart': 'Mar',
            'april': 'Apr',
            'mei': 'May',
            'juni': 'Jun',
            'juli': 'Jul',
            'augustus': 'Aug',
            'september': 'Sep',
            'oktober': 'Oct',
            'november': 'Nov',
            'december': 'Dec'
        }

        def __init__(self):
            # initializations
            self.session = requests.Session()
            self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
            self.MAIN_URL = 'http://www.vakantiediscounter.nl'
            self.BASE_URL = 'http://www.vakantiediscounter.nl/zonvakantie'
            self.countries = {}  # This dict will hold countries name with their values
            # self.driver = webdriver.Firefox()

  
        def scrape_deals(self, country):
            # Get the deal page
            deal_url = self.MAIN_URL+"/"+country
            resp = self.session.get(deal_url)
            soup = BeautifulSoup(resp.text)
            ADMIN_DATA = []
            
            tbl_price =soup.findAll("div", { "class" : "l landingpage__variation__content__accommodation_wrapper" })
            if tbl_price:
                list_accom = tbl_price[1].findAll('a',{'class':'o block landingpage__variation__content__accommodation_element landingpage__variation__content__accommodation_element__gutter'})
                
                for item in list_accom:
                    data_dict = {}
                    
                    staying = item.find('span',{'class':'l block landingpage__variation__content__accommodation__description-wrapper'}).find(text=re.compile(r'dagen'))
                    staying = re.findall(r'\d+', staying)
                    if  staying:
                        #print staying
                        staying = staying
                    else:
                        staying = None
                    likes = item.find('span',{'class':'l block landingpage__variation__content__accommodation_score'})
                    if likes:
                        likes = likes.text
                    else:
                        likes = None
                    # Construct the date string
                    date = item.find('span',{'class':'description block'}).text
                    ds = date.strip().split(', ')[-1]
                    day, month, year = ds.split()
                    month = self.MONTHS[month]
                    date_string = '%s-%s-%s' % (day, month, year)
                    # Add this to the data_dict
                    data_dict = {'title':item.find('span',{'class':'l link'}).text,
                                'deeplink':self.MAIN_URL+item['href'],
                                'country':country,
                                'days_of_staying':staying[0],
                                'date':date_string,
                                'likes': likes,
                                'price':item.find('span',{'class':'r bold block price-label-small'}).text
                    }
                    ADMIN_DATA.append(data_dict)
            return ADMIN_DATA


def execute(country):

        scraper = Vakantie()
        data = []
        deal = scraper.scrape_deals(country)
        #print deal
        for item in deal:
            #print item
            fmdate = datetime.strptime(item['date'], '%d-%b-%Y') 
            d = {
                    'title': item['title'],
                    'deeplink': item['deeplink'],
                    #'likes': item['likes'],
                    'zoover_score': item['likes'],
                    'date': fmdate,
                    'price': int(item['price'].split()[-1]),
                    'country': item['country'],
                    'persons': 2,
                    'days_of_staying': int(item['days_of_staying'])
            }
            data.append(d)
            #print d
        return data


#print execute('portugal/algarve.htm')

# countries = {'bulgarije':'250','curacao':'500','cyprus':'300','egypte':'250','gambia':'550','griekenland':'199',
                #'macedonie':'199','portugal':'250','spanje':'250','tunesie':'300','turkije':'200'
                #}
