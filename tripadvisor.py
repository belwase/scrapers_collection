# -*- coding: utf-8 -*-
# -- coding: utf-8 --

from pyvirtualdisplay import Display
from itertools import islice
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from random import random
import requests
import json
import re
import os
import time
import csv
from datetime import datetime
import codecs


class Tripadvisor():

	def __init__(self):

		self.BASE_URL = 'http://www.tripadvisor.com'
		#self.LOC_URL = 'http://www.tripadvisor.com/Attractions-g2-Activities-oa{}-Asia.html#LOCATION_LIST'
		self.LOC_URL = 'http://www.tripadvisor.com/Attractions-g147400-Activities-c55-oa{}-U_S_Virgin_Islands.html#LOCATION_LIST'
		self.Ajax_Url = 'http://www.tripadvisor.com/AttractionsAjax-{}.html'

		self.session = requests.Session()
		self.user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36'}
		self.writer = None
		

		display = Display(visible=0, size=(1024, 768))
		display.start()

		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.91 Safari/537.36'
		dcap["phantomjs.page.settings.resourceTimeout"] = '9000'
		self.driver = webdriver.Firefox()#PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
		self.driver.set_page_load_timeout(15)
		self.driver.set_script_timeout(10)

		with open("boats-virgin_america.csv", "w") as f:
			try:
				#For business
				headers = ["name", "address", "phone", 'website', "email", "description","url","attraction","state","country"]
				#For city
				#headers = ["url","attraction","state"]
				self.writer = csv.DictWriter(f, headers,quotechar='"')
				self.writer.writeheader()
			except:
				pass

	def __del__(self):
		self.driver.quit()
		#display.stop()


	def save_to_csv(self,data):
		with open("boats-virgin_america.csv", "a") as f:
			try:
				headers = ["name", "address", "phone", 'website', "email", "description","url","attraction","state","country"]
				writer = csv.DictWriter(f, headers)
				for key, value in data.items():
					data[key] = value.encode('ascii', 'ignore')
				try:
					writer.writerow(data)
				except Exception, e:
					print e.message
					#continue
			except Exception, e:
				print e.messag
				data = {'name': '', 'address': '', 'email': '','website':'', 'phone': '','description':'', 'url': data['url'],'attraction':'','state':'',}
				pass

	def save_boat_to_csv(self,data):
		with open("boat.csv", "w") as f:
			try:
				headers = ["name","attraction","state","present"]
				writer = csv.DictWriter(f, headers)
				for key, value in data.items():
					data[key] = value.encode('ascii', 'ignore')
				try:
					writer.writerow(data)
				except Exception, e:
					print e.message
					#continue
			except Exception, e:
				print e.messag
				data = {'name': '','attraction':'','state':'','present':''}
				pass
				
	def get_website(self):
	
		csvFile = csv.reader(open("input.csv", "rb"))
		for row in islice(csvFile,14015,None):
			try:
				print row[0]
				url =  row[4]
				if 'http' not in url:
					#print url
					self.driver.get('http://localhost/test.html?x='+url)
					element = self.driver.find_element_by_xpath(".//*[@id='box']")
					website = element.get_attribute("value")
					#print website
					self.driver.get(self.BASE_URL+website)
					website = self.driver.current_url
					print website				
					fp = open('websites','a')
					fp.write(row[0]+','+website+'\n')
					#fp.close()
					#print website
				#break
			except:
				#fp = open('websites','a')
				#fp.write(row[0]+','+row[1]+'\n')
				#fp.close()
				continue

				
				

		

	def save_city_to_csv(self,data):
		with open("city-virgin_america.csv", "a") as f:
			try:
				headers = ["url","attraction","state"]
				writer = csv.DictWriter(f, headers)
				for key, value in data.items():
					data[key] = value.encode('ascii', 'ignore')
				try:
					writer.writerow(data)
				except Exception, e:
					print "Err",e.message
					#continue
			except Exception, e:
				print e.messag
				#data = {'url': data['link'], 'attraction': '', 'state': ''}
				pass


	def get_location(self):

		for page in range(20,370,50):
			page_url = self.LOC_URL.replace("{}",str(page))
			print page,page_url
			response = self.session.get(page_url, headers=self.user_agent)
			soup = BeautifulSoup(response.text)
			geo_list = soup.find('ul',{'class':'geoList'}).findAll('li')
			for loc in geo_list:
				try:
					
					location = loc.find('a').text
					link = loc.find('a')['href']
					state = loc.find('span').text
					#Store urls to file
					data = {"attraction":location,"url":link,"state":state}
					#print data
					self.save_city_to_csv(data)
				except:
					continue
			#break
		#pass

	def get_business_info(self,biz_url,attraction,state):
		print biz_url,attraction,state
		try:
			response = self.session.get(biz_url,headers=self.user_agent)
		except:
			return
		soup = BeautifulSoup(response.text)
		business_links = soup.findAll('div',{'class':'property_title'})
		for biz in business_links:
			print biz.find('a')['href']
			biz_deep_url = self.BASE_URL + biz.find('a')['href']
			response = self.session.get(biz_deep_url , headers = self.user_agent)
			soup = BeautifulSoup(response.text)

			try:
				business_name = soup.find('h1',{'class':'heading_name'}).text
				#print business_name
			except:
				business_name = ''
			try:
				address = soup.find('span',{'class':'format_address'}).text.split('Address:')[1]
				#print address
			except:
				address = ''
			try:
				phone = soup.find('div',{'class':'phoneNumber'}).text.split('Phone Number:')[1]
				#print phone
			except:
				phone = ''

			try:
				description = soup.findAll('div',{'class':'details_wrapper'})[-1].text.split('Description:')[1]
				#print description
			except:
				description = ''

			try:
				regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
				email_div = soup.findAll('div',{'class':'taLnk hvrIE6 fl'})
				#print email_div
				#print email_div[1].attrs['onclick']
				for email_d in email_div:
					if 'Email' in email_d.attrs['onclick']:
						email_div = email_d
				#print email_div[-1]
				#print email_div
				email = re.findall(regex,str(email_div))
				email = email[0][0]
				#print email
			except Exception as e:
				email = ''
				print e.message

			try:
			
				website_div = soup.find('span',text='Website')
				#print website_div
				web_code = website_div.attrs['onclick'].split("aHref':'")#[1].split("'")[0]
				web_code =  web_code[1].split("'")[0]
				#print web_code
				website = web_code
			
				#response = self.session.get('http://localhost/test.html?x='+website)
				#print response.text
				#soup = BeautifulSoup(response.text)
				#website = soup.find('input',{'name':'box'}).attrs['value']	
				'''	
				self.driver.get('http://localhost/test.html?x='+web_code)
				element =  self.driver.find_element_by_xpath(".//*[@id='box']")
				website = element.get_attribute("value")
				self.driver.get(self.BASE_URL+website)
				#time.sleep(2)
				website = self.driver.current_url
				
				print website
				#self.driver.close()
				#driver.quit()
				'''
			except:
				website = ''

			try:
				country = soup.find('input',{'id':'GEO_SCOPED_SEARCH_INPUT'}).attrs['value']
				print country
			except:
				country = ''

			data = {'name': business_name, 'address': address, 'email': email,'website':website, 'phone': phone,'description':description, 'url': biz_deep_url,'attraction':attraction,'state':state,'country':country}
			#print data
			self.save_to_csv(data)

	def check_boat(self):
		csvFile = csv.reader(open("all_location.csv", "rb"))
		for row in csvFile:
			#print row[0],row[1],row[2]
			#Convert to boats and service url
			#check for boats
			url = self.BASE_URL + row[0]
			
			response = self.session.get(url,headers=self.user_agent)
			soup = BeautifulSoup(response.text)
			categories = soup.findAll('div',{'class':'filter filter_xor '})
			#print categories
			boats = False
			for cat in categories:
				cat_text = cat.find('span',{'class':'filter_name'}).text.lower()
				#print cat_text
				if 'boat' in cat_text:
					print 'Found'
					boats = True
					
			if boats  == True:
				data = {'url':row[0],'attraction':row[1],'state':row[2],'present':'True'}
				
			else:
				data = {'url':row[0],'attraction':row[1],'state':row[2],'present':'False'}

			self.save_boat_to_csv(data)

			

	def get_business(self):
		csvFile = csv.reader(open("city-virgin_america.csv", "rb"))
		for row in csvFile:
			print row[0],row[1],row[2]
			
			#check for boats
			url = self.BASE_URL + row[0]
			print url			
			response = self.session.get(url,headers=self.user_agent)
			
			soup = BeautifulSoup(response.text)
			try:
				categories = soup.findAll('div',{'class':'filter filter_xor '})
				#print categories
			except:
				continue
				
			boats = False
			for cat in categories:
				cat_text = cat.find('span',{'class':'filter_name'}).text.lower()
				#print cat_text
				if 'boat' in cat_text:
					print 'Found'
					boats = True
					
			if boats  == False:
				continue
			
			url = url.replace("Activities-","Activities-c55-")
			print url
			try:
				response = self.session.get(url,headers=self.user_agent)
			except:
				continue
			soup = BeautifulSoup(response.text)
			#check for pagination
			try:
				pagination = soup.find('div',{'class':'pagination'}).findAll('a',{'class':'paging taLnk '})
				pages =  pagination[-1].text
				print pages
				for page in range(0,int(pages)*30,30):
					back_part = url.split('-',1)[1]
					back_part = back_part.replace("c55","c55-oa"+str(page))
					#"g294226-Activities-c55-oa00-Bali"
					biz_url = self.Ajax_Url.replace("{}",back_part)
					print biz_url
					self.get_business_info(biz_url,row[1],row[2])
					#break
					#Now get all items
					
			except Exception as e:
				print 'no pagination',e.message
				#print 'moving to ',url
				self.get_business_info(url,row[1],row[2])
				#print 'moved'


ta = Tripadvisor()
#ta.get_location()
#ta.get_business()
for page in range(0,270,30):
	ta.get_business_info('http://www.tripadvisor.com/Attractions-g147400-Activities-c55-oa%s-U_S_Virgin_Islands.html'%page,'Virgin Attractions','Virgin Island')
#ta.get_website()
