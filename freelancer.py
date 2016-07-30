import logging
import os
import json
from re import findall, compile
from grab import Grab
from grab.spider import Spider, Task

r_balance = compile(r'open_purchases":{"value":([\d.]*?),')
session_f_name = 'freelancer_session.txt'


def parse(regex, body, _from=0, size=None):
    val = findall(regex, body)
    length = len(val)
    if length > 0:
        if length == 1:
            return val[0]
        else:
            return val[_from:size]
    else:
        return -1


def create_session(url, username, password, session_file='cookie_session.txt', update_session=False):
	if update_session:
		if os.path.isfile(session_file):
			os.remove(session_file)

	if not os.path.isfile(session_file):
		open(session_file, 'a')
		g = Grab()
		g.setup(cookiefile=session_file)
		resp = g.go(url,post={'username': username, 'passwd': password, 'savelogin': 'on'})
		print resp.body
		if json.loads(resp.body)['status'] == 'success':
			print 'Yes'
        #print g.cookies.cookiejar


class FreelancerSpider(Spider):
	items_cache = dict()
	target_urls = None
	session_file = None

	def update_grab_instance(self, grab):
		# use the session file
		if self.session_file:
			grab.setup(cookiefile=self.session_file)

	def task_generator(self):
		for url in self.target_urls:
			yield Task('page', url=url, initial=True)

	def task_page(self, grab, task):
		if grab.response.code == 200:
			body = grab.response.body
			#print body
			file_ = open('freelancer', 'w')
			file_.write(body)
			file_.close()
			try:
				data = json.loads(body)
				
				'''
				balance = grab.doc.select(".//*[@id='freelancer-stats']")
				print balance
				print balance.text()
				'''
			except Exception as e:
				print e.message
			info = {'balance': data['report']['balance']}
			print info
			self.items_cache['info'] = info
			pprint(self.items_cache)
		else:
			print('Not found %s' % grab.response.url)

     

def scrape(url,session_file=None):
	spider = FreelancerSpider(thread_number = 3)
	if type(url) is str:
		spider.target_urls = [url]
	elif hasattr(url, '__iter__'):
		spider.target_urls = url
	else:
		logging.log(logging.ERROR, 'unsupported type: ' + str(type(url)))
	spider.session_file = session_file
	spider.run()
	return spider.items_cache
	




if not os.path.isfile(session_f_name):
	create_session('https://www.freelancer.com/users/ajaxonlogin.php', USERNAME, PASSWORD, session_f_name)
	scrape('https://www.freelancer.com/ajax/finance/getFinancialReport.php', session_f_name)
