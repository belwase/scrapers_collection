# -*- coding: utf-8 -*-
# -- coding: utf-8 --

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



session = requests.Session()

base_url = 'http://www.yellowpages.ca'

#with location
#http://www.yellowpages.ca/search/si/1/Grill%20It%20Up/Brampton%2C%20ON

url = 'http://www.yellowpages.ca/search/si/1/' #Ginger%20Esthetic%20&%20Nail%20Studio/Toronto%2C%20ON'

user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36'}


def get_data(name):

	response = session.get(url+name+"/Toronto%2C%20ON",headers=user_agent)

	soup = BeautifulSoup(response.text)
	next_page = False
	try:

		products = soup.findAll('div',{'class':'listing'})
		first_product = products[0].find('a').attrs['href']
		product_url = base_url+first_product
		if product_url:
			next_page = True
		print product_url
	except:
		print 'no items'

	if next_page:

		#Open the page & scrape info
		print 'scraping....' + product_url
		try:
			response = session.get(product_url,headers=user_agent)
		except:
			pass
		soup = BeautifulSoup(response.text)
		content = soup.findAll('div',{'class':'detailInfo'})
		category = ''
		product = ''
		try:
			description = soup.find('article',{'class':'merchantHead-description'}).text
			try:
				description = description.split('More...')[0]
			except:
				try:
					description = description.split('.')
					description = '_'.join(description[:2]), '_'.join(description[2:])
				except:
					pass

		except:
			description = ''
			pass
		for element in content:
			header = element.find('h3')
			if 'Categories' in header.text:
				#print 'cat'
				category = element.findAll('li')[0].text
			elif 'Products and Services' in header.text:
				#print 'product'
				product = element.findAll('li')[0].text

		return {'name':name.strip(), 'product':product.strip(),'category':category.strip(),'description':description.strip()}

	return {'name':name.strip(), 'product':'','category':'','description':''}


Result = []


#for line in fileinput.input(['data'],encoding='utf-8'):
#	Result.append(get_data(line.strip())) #Salon Jodia Inc

with codecs.open('data','r',encoding='utf-8') as input_file:
	c = 1
	for line in input_file:
		print c
		c = c +1
		Result.append(get_data(line.strip()))
		#if c ==3:
		#	break


#print Result

headers = ["name","category","product","description"]
#print CSV
with open("output.csv", "w") as f:
    try:
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        #writer.writerow(headers)
        for row in Result:
            for key,value in row.items():
                row[key] = value.encode('ascii','ignore')
            try:
            	writer.writerow(row)
            except:
            	continue
    except Exception, e:
        print e

#print response.text
#with open('output.text','w') as output:
#	output.write(response.text.encode('ascii','ignore'))


