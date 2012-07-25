import os
import pymongo

from bottle import TEMPLATE_PATH, route, jinja2_template as template, request, response
from models import *
from bottle import static_file
import urllib
import urllib2
import sys
sys.path.append('./backend/feeds')
sys.path.append('./backend/feeds/feedconvertors/craigslist')
import feedslib
import feedsconfig
import json
from BeautifulSoup import BeautifulSoup
import unicodedata
import CLJsonFeed
TEMPLATE_PATH.append('./templates')

DBNAME = "test"
PRICE_HIGH_PER = 0.15
PRICE_LOW_PER = 0.25


	
@route('/jquery-ui-1.8.21.custom/<dir1>/<dir2>/<dir3>/:filename')
def serve_jquery_ui_3(dir1,dir2,dir3,filename):
	return static_file(dir1 + '/' + dir2 + '/' + dir3 + '/' + filename, root='./jquery-ui-1.8.21.custom/')
	
@route('/jquery-ui-1.8.21.custom/<dir1>/<dir2>/:filename')
def serve_jquery_ui_2(dir1,dir2,filename):
	return static_file(dir1 + '/' + dir2 + '/' + filename, root='./jquery-ui-1.8.21.custom/')
	
@route('/jquery-ui-1.8.21.custom/<dir1>/:filename')
def serve_jquery_ui_1(dir1,filename):
	return static_file(dir1 + '/' + filename, root='./jquery-ui-1.8.21.custom/')

@route('/siteassets/<dir1>/:filename')
def serve_static(dir1, filename):
    return static_file(dir1 + '/' + filename, root='./siteassets/')
    
@route('/bootstrap/<dir1>/<dir2>/<dir3>/:filename')
def serve_static(dir1, dir2, dir3, filename):
    return static_file(dir1 + '/' + dir2 + '/' + dir3 + '/' + filename, root='./bootstrap/')

@route('/')
def hello_world():
    return "Hello World!!!!"
    
@route('/getclfeed/<keyword>/<pricelow>/<pricehigh>/<pageindex>/<zipcode>/<city>/<state>')
def getclfeed(keyword,pricelow,pricehigh,pageindex,zipcode,city,state):
	jsonresp = CLJsonFeed.getCLJson(keyword,pricehigh,pricelow,pageindex,zipcode,city,state,DBNAME)
	return jsonresp

@route('/:username')
def user(username):
    users_table = pymongo.Connection('localhost', 27017)[DBNAME]['users']
    if not users_table.find_one({'username': username}):
        return 'User %s not a part of our beta test. Please wait for your invite :-)' % username
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
    deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
    queries = [query for query in mainbox_table.find({'username': username})]
    deals = []
    qlen = len(queries)
    if len(queries) > 0:
        first_query = queries[0]
        deals.extend([deal for deal in deals_table.find({'query_id': first_query['_id']})])
    response.set_cookie('username', username, path = '/')    
    return template('userhome.html', username = username, queries = queries, deals = deals, qlen = qlen, PRICE_HIGH_PER = PRICE_HIGH_PER, PRICE_LOW_PER = PRICE_LOW_PER)

import string
@route('/addquery/<keyword>/<dollarlimit>')
def addquery(keyword, dollarlimit):
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
    username = request.cookies.get('username')
    queries = [query for query in mainbox_table.find({'username': username})]
    
        
    dollar = int(dollarlimit)
    keyword = string.strip(keyword)
    pricehigh = int(dollar + (PRICE_HIGH_PER * dollar))
    pricelow = int(dollar - (PRICE_LOW_PER * dollar))
    pricemax = pricehigh * 2
    pricemin = pricelow / 2
    queryhash = feedslib.gethash(keyword + dollarlimit + str(pricehigh) + str(pricelow))
    querymatches = [query for query in mainbox_table.find({'_id': queryhash})]
    if(len(querymatches) == 0):
   		mainbox_table.insert({'_id': queryhash, 'username': username, 'keyword': keyword, 'dollar_limit': dollarlimit, 'price_high': pricehigh, 'price_low': pricelow, 'lastmodified': datetime.utcnow(), 'dayfilter': 7, 'pricemax': pricemax, 'pricemin': pricemin})
   		
		try:
			results1 = feedslib.getFeedDeals("craigslist", feedsconfig.CONFIG, keyword, pricehigh, pricelow, "","95051","Santa Clara","CA")
			deals1 = results1['deals']
			print "feed1 deals found: " + str(len(deals1))
			results2 = feedslib.getFeedDeals("google", feedsconfig.CONFIG, keyword, pricehigh, pricelow, 25)
			deals2 = results2['deals']
			print "feed2 deals found: " + str(len(deals2))
			deals = deals1 + deals2
			print "Total deals found: " + str(len(deals))
			
			sys.stdout.flush()
			if(len(deals) > 0):
				deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
				print "Inserting into deals table..."
				sys.stdout.flush()
				deals_table.insert(deals)
		except TypeError, ex:
			print "TypeError: ", ex
		except:
			print "Unexpected error:", sys.exc_info()[0]
   		
    
    return {'status': 'ok'}

from datetime import datetime
import sys
@route('/getdealemail/<keyword>/<dollarlimit>/<days>/<username>')
def getdealemail(keyword, dollarlimit, days, username):
    dollarlimit = int(dollarlimit)
    dollarlimit = int(1.25 * dollarlimit) 
    daylimit = int(days);
    deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
    deals = []
    dealsout = []
    deals.extend([deal for deal in deals_table.find({'keyword': keyword, 'price': {'$lt': dollarlimit} }).sort("founddate", pymongo.DESCENDING)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        d = (datetime.utcnow() - d2).days
       
        if(d > daylimit):
            break
        deals[i]['days'] = d
        dealsout.insert(i, deals[i])
        i = i + 1
    deals = dealsout
    sys.stdout.flush()
    return template('getdealemail.html', username = username, keyword = keyword, dollarlimit = dollarlimit, deals = deals)


@route('/getfilters/<queryid>')
def getfilters(queryid):
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
    query = mainbox_table.find_one({'_id': queryid})   
    return template('getfilters.html', query = query)

@route('/getdeals/<keyword>/<dollarlimit>/<pricehigh>/<pricelow>/<startnum>/<resultsize>/:filename')
def getdeals(keyword, dollarlimit, pricehigh, pricelow, startnum, resultsize, filename):
    dollarlimit = int(dollarlimit)
    pricehigh = int(float(pricehigh))
    pricelow = int(float(pricelow))
    startnum = int(startnum) - 1
    resultsize = int(resultsize)
    deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
    deals = []
    if(dollarlimit == -1):
        sys.stdout.flush()
        mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
        queries = [query for query in mainbox_table.find({'username': keyword})]  
        qlen = len(queries)
        if(qlen == 0):
            return ""
        else:
            keyword = queries[0]['keyword']
            dollarlimit = int(queries[0]['dollar_limit'])
            pricehigh = int(queries[0]['price_high'])
            pricelow = int(queries[0]['price_low'])
            print keyword + ":" + str(dollarlimit) + "\n"
            sys.stdout.flush()
   
    
    deals.extend([deal for deal in deals_table.find({'keyword': keyword, 'price': {'$lt': pricehigh}, 'price': {'$gt': pricelow} }).sort("founddate", pymongo.DESCENDING).skip(startnum).limit(resultsize)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        days = (datetime.utcnow() - d2).days
        deals[i]['days'] = days
        i = i + 1
    sys.stdout.flush()
    return template(filename, keyword = keyword, dollarlimit = dollarlimit, deals = deals)
    
"""@route('/getsaveddeals/<mainboxid>/')
def getsaveddeals(mainboxid):
   
    deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
    deals = []
   
	saveddeals_table = pymongo.Connection('localhost', 27017)[DBNAME]['saveddeals']    
	queries = [query for query in mainbox_table.find({'mainboxid': mainboxid})]  
	qlen = len(queries)
	if(qlen == 0):
		return ""

    
    deals.extend([deal for deal in deals_table.find({ "_id": { $in: queries } }).sort("founddate", pymongo.DESCENDING)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        days = (datetime.utcnow() - d2).days
        deals[i]['days'] = days
        i = i + 1
    print deals
    sys.stdout.flush()
    return template('getdeals.html', keyword = keyword, dollarlimit = dollarlimit, deals = deals)
"""
    
@route('/getqueries/<username>/<linkno>')
def getqueries(username, linkno):
    linkno = int(linkno)
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
    queries = [query for query in mainbox_table.find({'username': username})]  
    qlen = len(queries)  
    return template('getqueries.html', username = username, linkno = linkno, queries = queries, qlen = qlen)

@route('/getpopularqueries/<username>/<linkno>')
def getpopularqueries(username, linkno):
    linkno = int(linkno)
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
    queries = [query for query in mainbox_table.find().limit(6)]  
    qlen = len(queries)  
    return template('getpopularqueries.html', username = username, linkno = linkno, queries = queries, qlen = qlen)
    

@route('/removequery/<username>/<dollar_limit>/<keyword>')
def removequery(username, dollar_limit, keyword):
    
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
    #did = bson.objectid.ObjectId(qid)
    
    mainbox_table.remove({'username': username, 'dollar_limit': dollar_limit, 'keyword': keyword})
    print "Removing| dollarlimit:" + str(dollar_limit) + ", keyword: " + keyword + "\n"
    sys.stdout.flush()
    return {'status': 'ok'}
