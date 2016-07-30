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

base_url = 'www.cylex.ca'

url = 'http://www.cylex.ca/s?q=grill%20it%20up&c=brampton&z=&p=1&dst=&cUrl=' 

user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36'}


def get_url(name,city):
	return 'http://www.cylex.ca/s?q='+name+'&c='+city+'&z=&p=1&dst=&cUrl='

def get_data(auth_url):
	#url = get_url(name,city,auth_url)
	#print 'scrapping...'+auth_url
	#response = session.get(url,headers=user_agent)
	proxy = { 
              "http"  : '67.239.73.60:8080'
            }

	cylex_present = False
	try:
		if 'cylex' in auth_url:
			cylex_present = True
	except:
		print 'no items'
		
	if cylex_present:

		#Open the page & scrape info
		print 'scraping....' + auth_url
		content = ''
		try:

			response = session.get(auth_url,headers=user_agent,proxies=proxy)
			#print response.text
			soup = BeautifulSoup(response.text)
			content = soup.findAll('section',{'class':'msnry-item w2'})
			for item in content:
				if 'Description' in item.text:
					content = item
					break
		except:
			pass

		try:
			name = soup.find('div',{'id':'cntct-name'}).text
		except:
			name = ''

		try:
			product = content.find('span',{'class':'truncated-200'}).text
			product = product.split(',')[0]
		except:
			product = ''
			pass

		try:
			print 'here'
			category_content = content.findAll('ol',{'class':'breadcrumb'})[0]
			category = category_content.findAll('li',{'itemprop':'itemListElement'})[1].find('span',{'itemprop':'name'}).text
			#print category
		except:
			category = ''
			pass

		try:
			description = content.find('div',{'style':'margin-top:20px;'}).find('span',{'class':'truncated-200'}).text
			#print company_desc
		except:
			try:
				description = content.find('p',{'itemprop':'description'}).text
				#print description
			except:
				description = ''
				pass

		return {'name':name.strip(), 'product':product.strip(),'category':category.strip(),'description':description.strip()}

	return {'name':name.strip(), 'product':'','category':'','description':''}


Result = []


#for line in fileinput.input(['data'],encoding='utf-8'):
#	Result.append(get_data(line.strip())) #Salon Jodia Inc

with codecs.open('data','r',encoding='utf-8') as input_file:
	c = 0
	for line in input_file:
		c = c +1
		#if c ==2:
		#	break
		#name,auth_url = line.strip().split(',')
		print str(c) + ' : '  + line
		data = get_data(line.strip())
		print data
		if 'cylex' in line:
			time.sleep(3)
			#	break
		Result.append(data)

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


