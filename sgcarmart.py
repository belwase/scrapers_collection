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

base_url = 'http://www.sgcarmart.com/directory/listing.php?'#BRSR=0&CAT=7&RPG=15


user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36'}


def get_key_value(trs):
	data = {}
	print len(trs)
	data['name'] = trs[0].find('a').text
	for tr in trs[1:]:
		td = tr.findAll('td')
		try:
			key = td[0].text
			value = td[2].text
			#print key,value
			data[key] = value
		except:
			continue
	#Try for product and services
	#try:
	#	prod = tr[-1].findAll('div',{'id':'sgcarstore_item'})
	
	return data
		

def get_data():
	
	RESULT = []

	for page in range(450,1305,15): #1305
		url = base_url+"BRSR=%s&CAT=7&RPG=15"%page
		print url
		response = session.get(url,headers=user_agent)
		soup = BeautifulSoup(response.text, "lxml")
		merchants = soup.find('div',{'id':'merchantlisting'}).findAll('table',{'align':'center'})
		
		'''
		ratings_table = soup.findAll('td',{'width':'174'})
		print len(ratings_table)
		for rating in ratings_table:
			#Ratings
				try:
					print 'trying'
					rate = rating.find('span',{'class':'ratingstars_big'})
					#rate = re.findall(r'\d+',rate.attrs['class'][0] )
					rate = rate.attrs['class'][0]
					rate = rate[1]+'.'+rate[2]
					print rate
				except:
					pass
				
		return
		'''
		#print len(merchants)
		
		#return
		for merchant in merchants:
			
			try:
				
				tr_data =  merchant.findAll('tr')
				
				data = get_key_value(tr_data)
				
				
				RESULT.append(data)
				
			except:
				continue
			#break
			#return
		#print RESULT
	return RESULT
	

Result = get_data()

headers = ["name","Address","Opening Hours","Phone","Website","Category","Specialises in","Brands Carried","Description"] #,"ratings"]
#print CSV
with open("sgcarmart-data.csv", "w") as f:
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


