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
import sys

class Facebook():

	def __init__(self):

		self.MAIN_URL = 'https://www.facebook.com'
		self.PAGE_URL = 'https://www.facebook.com/search/pages/?q='
		self.session_file = 'session.txt'
		
		#self.display = Display(visible=0, size=(800, 600))
		#self.display.start()

		profile = webdriver.FirefoxProfile()
		profile.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36")
		profile.set_preference("intl.accept_languages","en-US, en")
		profile.set_preference("network.http.accept.default","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")
		self.driver = webdriver.Firefox(profile)
		
		self.write = None
		self.output = 'scrapped_data.csv'

	def __del__(self):
		#self.display.stop()
		self.driver.quit()
		
	def load_cookies(self):
		self.driver.get(self.MAIN_URL)
		cookies = pickle.load(open(self.session_file, "rb"))
		for cookie in cookies:
			self.driver.add_cookie(cookie)
		print 'Logged In'

	def create_session(self,username,password):
		if not os.path.isfile(self.session_file):
			self.driver.get(self.MAIN_URL)
			self.driver.find_element_by_id('email').send_keys(username)
			self.driver.find_element_by_id('pass').send_keys(password)
			self.driver.find_element_by_id('login_form').submit()
			time.sleep(2)
			pickle.dump(self.driver.get_cookies() , open(self.session_file,"wb"))
		else:
			self.load_cookies()

	def crawl(self,keyword):
		pageLinks = []
		self.driver.get(self.PAGE_URL+keyword)
		time.sleep(2)
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		#fp = open('source.html','w')
		#fp.write(self.driver.page_source.encode('ascii', 'ignore'))
		#time.sleep(60)
		#soup = BeautifulSoup(self.driver.page_source,"lxml")
		source = self.driver.page_source.encode('ascii', 'ignore')
		result = re.findall('(facebook.com(.){100})',source) #x = re.findall('(facebook.com\/\w{0,100})',fp)
		for item in result:
			print item
		

fb = Facebook()
fb.create_session(EMAIL, PASSWORD)
fb.crawl('boats in thailand')  

#https://www.facebook.com/search/pages/?q=boats%20in%20thailand
