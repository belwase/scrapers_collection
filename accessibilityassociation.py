#!/usr/bin/python
#-*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import json
import os
import time
import pickle
from bs4 import BeautifulSoup
import re
import math
import csv

class AccessibilityAssociation():

	def __init__(self):

		self.LOGIN_URL = 'http://www.accessibilityassociation.org/login.asp'
		self.MEMBER_URL = 'http://connections.accessibilityassociation.org/network/members/advanced-search'
		self.session_file = 'session.txt'
		
		self.display = Display(visible=0, size=(800, 600))
		self.display.start()

		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36")
		profile.set_preference("intl.accept_languages","en-US, en")
		profile.set_preference("network.http.accept.default","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
		self.driver = webdriver.Firefox(profile)
		
		self.write = None
		self.output = 'accessibilityAssoc_members.csv'

	def __del__(self):
		self.display.stop()
		self.driver.quit()
		
	def load_cookies(self):
		self.driver.get(self.LOGIN_URL)
		cookies = pickle.load(open(self.session_file, "rb"))
		for cookie in cookies:
			self.driver.add_cookie(cookie)
		print 'Logged In'

	def create_session(self,username,password):
	
		if not os.path.isfile(self.session_file):
			self.driver.get(self.LOGIN_URL)
			self.driver.find_element_by_id("loginname").send_keys(username)
			self.driver.find_element_by_id("loginpassword").send_keys(password)
			self.driver.find_element_by_xpath(".//*[@id='login']/fieldset/div[3]/button").click()
			time.sleep(2)
			pickle.dump(self.driver.get_cookies() , open(self.session_file,"wb"))
		else:
			self.load_cookies()
	
	def save_to_csv(self,data):
		with open(self.output, "a") as f:
			try:
				headers = ["name", "email", "company", 'title', "address", "country"]
				writer = csv.DictWriter(f, headers)
				for key, value in data.items():
					data[key] = value.encode('ascii', 'ignore')
				try:
					writer.writerow(data)
				except Exception, e:
					print e.message
					#continue
			except Exception, e:
				print e.message
				pass
	
	
	def scrape(self,soup):
		print 'scrapping..'
		tableDirectory = soup.find('table',{'class':'table-directory'})
		trList = tableDirectory.findAll('tr')
		for tr in trList:
			try:
				name = tr.find('a',{'id':re.compile('^MainCopy_ctl15_Contacts_DisplayName')}).text
			except Exception as e:
				print e.message
				name = ""
			
			try:
				email = tr.find('a',{'id':re.compile('^MainCopy_ctl15_Contacts_EmailAddress')}).text
			except:
				email = ""
			try:
				company = tr.find('div',{'id':re.compile('^MainCopy_ctl15_Contacts_CompanyNamePanel')}).text
			except:
				company = ""
			try:
				title = tr.find('div',{'id':re.compile('^MainCopy_ctl15_Contacts_CompanyTitlePanel')}).text
			except:
				title = ""
			try:
				address = tr.find('div',{'id':re.compile('^MainCopy_ctl15_Contacts_Addr1Panel4')}).text
			except:
				address = ""
			try:
				country = tr.find('div',{'id':re.compile('^MainCopy_ctl15_Contacts_Addr1Panel5')}).text
			except:
				country = ""
				
			data = { 'name':name.strip(),'email':email.strip(),'company':company.strip(),'title':title.strip(),'address':address.strip(),'country':country.strip()}
			print data
			self.save_to_csv(data)

			
	def crawl(self,letter):
		self.driver.get(self.MEMBER_URL)
		#Try with initial of firstname 'a'
		self.driver.find_element_by_id("MainCopy_ctl06_FindFirstName").send_keys(letter)
		#click Find
		self.driver.find_element_by_id("MainCopy_ctl15_FindContacts").click()
		time.sleep(2)
		soup = BeautifulSoup(self.driver.page_source,"lxml")
		
		pageRe = re.compile('\d+')
		spanText = soup.find('span',{'id':'MainCopy_ctl15_ShowingLabel'}).text
		totalItems = re.findall(pageRe,spanText)
		maxPages = int(math.ceil(int(totalItems[-1])/20.0))
		print maxPages
		for i in range(1,maxPages+1):
			#self.driver.find_element_by_id('MainCopy_ctl15_Pager_Repeater1_pager_li_'+str(i)).click()
			link = self.driver.find_element_by_link_text("»")#(str(i))
			link.click()
			time.sleep(2)
			soup = BeautifulSoup(self.driver.page_source,"lxml")
			self.scrape(soup)
			print soup.find('span',{'id':'MainCopy_ctl15_ShowingLabel'}).text
		return
		
		

			


aa = AccessibilityAssociation()
aa.create_session(username,password)
#keyword = raw_input('Enter letter')
letters = ['m']
for letter in letters:
	aa.crawl(letter)
