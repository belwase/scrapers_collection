from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from selenium import webdriver
from django.conf import settings
from datetime import datetime
import requests
import uuid
import json
import time
import re
import os


class Arke(object):

    USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0'
    

    def __init__(self):
        self.session = requests.Session()
        self.session.headers[
            'User-Agent'] = self.USER_AGENT
        self.MAIN_URL = 'http://www.arke.nl'
        self.BASE_URL = 'http://www.arke.nl/zonvakantie'
        self.SEARCH_URL = 'http://www.arke.nl/data/search/result/facetsearch/'

        """
        fp = webdriver.FirefoxProfile()
        fp.set_preference("http.response.timeout", 60)
        fp.set_preference("dom.max_script_run_time", 60)
        fp.set_preference('permissions.default.image', 2)
        if os.path.exists('adblock.xpi'):
            adblock_path = 'adblock.xpi'
        else:
            adblock_path = settings.ADBLOCK_PATH
        fp.add_extension(adblock_path)
        self.display = Display()
        self.display.start()
        self.driver = webdriver.Firefox(firefox_profile=fp)
        """
        self.driver = webdriver.PhantomJS(service_args=['--load-images=false'])
        
 
    def pass_cookies_to_requests(self, driver):
        for c in self.driver.get_cookies():
            dp = {'domain': c['domain'], 'path': c['path']}
            self.session.cookies.set(c['name'], c['value'], **dp)
 
        
    def get_country_deals(self, country, persons=2):
        # Now go to each country page
        country_page = self.BASE_URL+"/"+country+"/resultaten/"
        self.driver.get(country_page)
        
        # Sort by prices
        sort_select = self.driver.find_element_by_id('segmentitem-change-sort')
        opts = sort_select.find_elements_by_tag_name('option')
        for opt in opts:
            if opt.text == 'Prijs vliegreis':
                opt.click()
        time.sleep(10)

        # Increase page size to 20 results per page
        pagesize_select = self.driver.find_element_by_id('segmentitem-change-pagesize')
        opts = pagesize_select.find_elements_by_tag_name('option')
        for opt in opts:
            if opt.text == '20 resultaten':
                opt.click()
        time.sleep(10)
        
        # Get the deals
        soup = BeautifulSoup(self.driver.page_source)
        items = soup.select('article.sr-item')

        deals = []
        for item in items:
            title = item.find('a', {'class':'acconame'}).text
            link = self.MAIN_URL + item.find('a', {'class':'btn'})['href']
            stars = item.select('div.classification span')
            if stars:
                star_rating = stars[0]['class'][0].strip('star')
            else:
                star_rating = None 
            prb_spans = item.select('div.pricebox span')
            days_of_staying = None
            departure_from = ''
            deal_type = ''
            for sp in prb_spans:
                if 'dagen' in sp.text:
                    days_of_staying = int(sp.text.split(' dagen')[0])
                    deal_type = sp.text.split(' - ')[-1].strip()
                elif 'Vertrek' in sp.text:
                    departure_from = sp.text.split('Vertrek ')[-1]
            d = {
                    'title': title, 
                    'link': link, 
                    'stars': star_rating,
                    'days_of_staying': days_of_staying,
                    'deal_type': deal_type,
                    'departure_from': departure_from
                }
            deals.append(d)
        
        if deals:
            # Use selenium to get cookies
            #print 'Fetching cookies using selenium (Firefox+Xvfb)...'
            try:
                self.driver.get(link)
                time.sleep(10)
                adults = self.driver.find_element_by_css_selector('select#adults')
                for opt in adults.find_elements_by_tag_name('option'):
                    if opt.text == str(persons):
                        opt.click()
                btn = self.driver.find_element_by_css_selector('div#rg-popup button.btn1')
                btn.click()
            except:
                pass
            
            # Get some cookies and pass to selenium
            for i in range(5):
                time.sleep(i * 0.1)
                cokie_names = [x['name'] for x in self.driver.get_cookies()]
                if '_TravelParty' in cokie_names:
                    self.pass_cookies_to_requests(self.driver)
                    break

        #print 'Closing Firefox and Xvfb...'
        self.driver.close()
        #self.display.stop()
 
        return deals

    
    def get_deal_page(self, deal_url, number_of_adults=2):
        # Set custom headers
        headers = self.session.headers
        headers['Host'] = 'www.arke.nl'
        headers['Referer'] = deal_url.strip('#prijzen')
        headers['X-Requested-With'] = 'XMLHttpRequest'
                
        # Get the deal page
        resp = self.session.get(deal_url, headers=headers)
        return resp

  
    def scrape_deal_page(self, deal_url):
        # Set custom headers
        headers = self.session.headers
        headers['Host'] = 'www.arke.nl'
        headers['Referer'] = deal_url.strip('#prijzen')
        headers['X-Requested-With'] = 'XMLHttpRequest'
                
        # Get the deal page
        resp = self.session.get(deal_url, headers=headers)
        
        # Get box price, price per person, and data url
        soup = BeautifulSoup(resp.text)
        data_url = soup.find('li',{'data-href':'#prijzen'})['data-url']
        data_url = self.MAIN_URL + data_url + '&_=%s' % int(time.time() * 100)
        
        # Scrape prices table
        resp = self.session.get(data_url)
        soup = BeautifulSoup(resp.text)
        prices_data = []
        grid = soup.find('table', {'id': 'grid'})
        if grid:
            dates = grid.find('thead').find_all('th')[1:-1]
            dates = [x.text for x in dates]
            for child in grid.children:
                if '>details<' in str(child):
                    row_prices = child.findChildren('td', recursive=False)[1:-1]
                    prices = []
                    for rp in row_prices:
                        try:
                            v = rp['class'][0].upper()
                        except KeyError:
                            try:
                                v = rp.find('span').text
                            except:
                                v = 'NA'
                        prices.append(v)
                    d = dict(zip(dates, prices))
                    prices_data.append(d)
        return prices_data
         
        
def execute(country):
    ADMIN_DATA = []
    for n in [2, 4]:
        scraper = Arke()
        deals = scraper.get_country_deals(country)
        for deal in deals:
            prices = scraper.scrape_deal_page(deal['link'])
            for pds in prices:
                for pd in pds:
                    date, price = pd, pds[pd]
                    year = datetime.now().year
                    date_string = '%s-%s' % (date[2:], year)
                    fmdate = datetime.strptime(date_string, '%d-%m-%Y')
                    d = {
                        'title': deal['title'],
                        'persons': n,
                        'deeplink': deal['link'],
                        'stars': int(deal['stars'])/10.0,
                        'date': fmdate,
                        'price': price,
                        'days_of_staying': deal['days_of_staying'],
                        'deal_type': deal['deal_type'],
                        'departure_from': deal['departure_from']
                    }
                    ADMIN_DATA.append(d)
    return ADMIN_DATA

      
        
"""
countries = {'aruba':'500','indonesie/bali':'819','bonaire':'500','cuba':'550',
                 'curacao':'500','cyprus':'250','dominicaanse-republiek':'599',
                 'verenigde-arabische-emiraten/dubai':'500','egypte':'275','gambia':'450','griekenland':'199',
                 'italie':'225','jamaica':'700','kaapverdie':'400','malta':'200',
                 'mexico':'500','thailand':'700','turkije':'190'
                 }
"""
