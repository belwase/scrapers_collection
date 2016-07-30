from bs4 import BeautifulSoup
from datetime import datetime
import requests
import time
import sys


class Stipreizen(object):
    
    
    def __init__(self):
        # initializations
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.MAIN_URL = 'http://www.stipreizen.nl'
        self.BASE_URL = 'http://www.stipreizen.nl/zonvakantie'


    def get_country_urls(self, country):       
        print "Now getting country accommodation........."
        urls = []
        response = self.session.get(self.BASE_URL+"/"+country)
        soup = BeautifulSoup(response.text)
        trip_list = soup.findAll('div', {'id':'price-tab-1'})
        for item in trip_list:
            urls.append(item.find('a')['href'])
        return urls


    def scrape_deal_page(self, deal_url):      
        # Get the deal page
        resp = self.session.get(deal_url)
        soup = BeautifulSoup(resp.text)
        ADMIN_DATA = []
        index = -2
        col_index = 0
        data_dict = {}
        tbl_price =soup.find("table", { "id" : "Table2" }).find("td",{"class":"tbl-price-left"})
        
        title = soup.find("section",{"class":"pc-txt-section fl"}).find("h3").text
        stars = title.count("*")/2
        title = title.replace("*","").strip()
        
        # Get zoover score
        score_div = soup.find('div', {'class': 'z-score'})
        if score_div:
            zs = score_div.find('script').text
            zs = zs.split("#dptab-zoover', '")[-1].split("'")[0]
            zoover_score = float(zs)
        else:
            zoover_score = None
        
        #Find values with given price
        for x in tbl_price.findAll('tr'):
            index = index+1
            if x.text=="8 dagen":
                tbl_price_right = soup.find("td",{"class":"tbl-price-right"}).find('tbody')
                for z in tbl_price_right.findAll('tr')[index].findAll('td'):
                    col_index = col_index + 1
                    data_dict[col_index]=z.text
                break
                
        #Now get the date for each cell value found
        date_head = soup.find("td", {"class":"tbl-price-right"}).find('thead').find('tr')
        date = date_head.findAll('th')
        for key,value in data_dict.iteritems():
            temp_dict = {}
            if len(value.strip())>1:
                temp_dict = {'title':title,'price':value,'date':date[key-1].text,'deeplink':deal_url,'stars':stars, 'zoover_score': zoover_score}
                ADMIN_DATA.append(temp_dict)
                #print ADMIN_DATA
        return ADMIN_DATA


def execute(country):
    scraper = Stipreizen()
    urls = scraper.get_country_urls(country)
    data = []
    for url in urls:
        try:
            deal = scraper.scrape_deal_page(url)
            #print deal
            for item in deal:
                #print item
                fmdate = datetime.strptime(item['date'][3:], '%d %b')
                d = {
                        'title': item['title'],
                        'deeplink': item['deeplink'],
                        'stars': item['stars'],
                        'zoover_score': item['zoover_score'],
                        'date': fmdate,
                        'days_of_staying': 8,
                        'price': int(item['price'])
                }
                data.append(d)
                #print d
        except AttributeError:
            pass
    return data


'''
if __name__ == '__main__':
    sr = Stipreizen();
    # countries = {'bulgarije':'250','curacao':'500','cyprus':'300','egypte':'250','gambia':'550','griekenland':'199',
                #'macedonie':'199','portugal':'250','spanje':'250','tunesie':'300','turkije':'200'
                #}
    # country = arke.get_list_of_all_countries()
    urls = sr.get_country_urls('curacao')
    print urls
    table_response = sr.scrape_deal_page(urls[0])
    print table_response

'''
#execute('bulgarije')
