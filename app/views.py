import os
import pymongo
import re
import string
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
from datetime import timedelta
TEMPLATE_PATH.append('./templates')

DBNAME = "test"
PRICE_HIGH_PER = 0.15
PRICE_LOW_PER = 0.25
PRICE_MAX_PER = 2
PRICE_MIN_PER = 2
DEFAULT_DAYS_FILTER = 7


	
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
    first_query = ""
    if len(queries) > 0:
        first_query = queries[0]
        deals.extend([deal for deal in deals_table.find({'query_id': first_query['_id']})])
    response.set_cookie('username', username, path = '/')    
    return template('userhome.html', username = username, queries = queries, deals = deals, qlen = qlen, PRICE_HIGH_PER = PRICE_HIGH_PER, PRICE_LOW_PER = PRICE_LOW_PER, DEFAULT_DAYS_FILTER = DEFAULT_DAYS_FILTER, PRICE_MAX_PER = PRICE_MAX_PER, PRICE_MIN_PER = PRICE_MIN_PER, first_query = first_query)



@route('/updatequerypricerange/<qid>/<pricelow>/<pricehigh>')
def updatequerypricerange(qid, pricelow, pricehigh):
	pricelow = int(pricelow)
	pricehigh = int(pricehigh)
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
	username = request.cookies.get('username')
	print "updating " + qid + ": " + str(pricelow) + " - " + str(pricehigh)
	sys.stdout.flush()
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "price_low" : pricelow , "price_high" : pricehigh } })
	print res
	sys.stdout.flush()
	return {'status': 'ok'}
	
@route('/updatequerydays/<qid>/<days>')
def updatequerydays(qid, days):
	days = int(days)
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
	username = request.cookies.get('username')
	print "updating " + qid + ": " + str(days) 
	sys.stdout.flush()
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "dayfilter" : days } })
	print res
	sys.stdout.flush()
	return {'status': 'ok'}
	
@route('/updatequeryfilters/<qid>/<filters>')
def updatequeryfilters(qid, filters):
	if(filters == "-1"):
		filters = ""
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
	username = request.cookies.get('username')
	print "updating " + qid + ": " + filters
	sys.stdout.flush()
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "filters" : filters } })
	print res
	sys.stdout.flush()
	return {'status': 'ok'}


@route('/addquery/<keyword>/<dollarlimit>')
def addquery(keyword, dollarlimit):
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
    username = request.cookies.get('username')
    queries = [query for query in mainbox_table.find({'username': username})]
    
        
    dollar = int(dollarlimit)
    keyword = string.strip(keyword)
    pricehigh = int(dollar + (PRICE_HIGH_PER * dollar))
    pricelow = int(dollar - (PRICE_LOW_PER * dollar))
    pricemax = pricehigh * PRICE_MAX_PER
    pricemin = pricelow / PRICE_MIN_PER
    queryhash = feedslib.gethash(username + keyword + dollarlimit + str(pricehigh) + str(pricelow))
    uniqqueryhash = feedslib.gethash(keyword + dollarlimit + str(pricehigh) + str(pricelow))
    querymatches = [query for query in mainbox_table.find({'_id': queryhash})]
    if(len(querymatches) == 0):
   		querymatches = [query for query in mainbox_table.find({'qid': uniqqueryhash})]
   		
   		if(len(querymatches) == 0):
			inserthash = {'_id': queryhash, 'qid': uniqqueryhash, 'username': username, 'keyword': keyword, 'dollar_limit': dollar, 'price_high': pricehigh, 'price_low': pricelow, 'lastmodified': datetime.utcnow(), 'dayfilter': DEFAULT_DAYS_FILTER, 'pricemax': pricemax, 'pricemin': pricemin}
			
			results1 = feedslib.getFeedDeals("craigslist", feedsconfig.CONFIG, keyword, pricehigh, pricelow, "","95051","Santa Clara","CA")
			deals1 = results1['deals']
			print "feed1 deals found: " + str(len(deals1))
			results2 = feedslib.getFeedDeals("google", feedsconfig.CONFIG, keyword, pricehigh, pricelow, 25)
			deals2 = results2['deals']
			print "feed2 deals found: " + str(len(deals2))
			deals = deals1 + deals2
			print "Total deals found: " + str(len(deals))
			
			tagcloudlist = [results1['tagcloud'], results2['tagcloud']]
			mtagcloud = feedslib.consolidateTagClouds(tagcloudlist)
			tagcloud = feedslib.getSortedTagCloudList(mtagcloud)
			tagslist = []
			facetcloudlist = [results1['facetcloud'], results2['facetcloud']]
			mfacetcloud = feedslib.consolidateTagClouds(facetcloudlist,4)
			facetcloud = feedslib.getSortedTagCloudList(mfacetcloud,12)
			facetslist = []
			for tag in tagcloud:
				inserthash[tag[0]] = tag[1]
				tagslist.append(tag[0])
			inserthash["tags"] = ','.join(tagslist)
			for facet in facetcloud:
				inserthash[facet[0]] = facet[1]
				facetslist.append(facet[0])
			inserthash["facets"] = ','.join(facetslist)
			sys.stdout.flush()
			if(len(deals) > 0):
				deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
				print "Inserting into deals table..."
				sys.stdout.flush()
				res = deals_table.insert(deals)
				print "Done inserting."
				sys.stdout.flush()
			
			
			print "Inserting query: " + str(inserthash)
			sys.stdout.flush()
			mainbox_table.insert(inserthash)
		else:
			thisquery = querymatches[0]
			thisquery['username'] = username
			thisquery['lastmodified'] = datetime.utcnow()
			thisquery['_id'] = feedslib.gethash(username + thisquery['keyword'] + str(thisquery['dollar_limit']) + str(thisquery['price_high']) + str(thisquery['price_low']))
			print "Inserting dup query: " + str(thisquery)
			sys.stdout.flush()
			mainbox_table.insert(thisquery)
   		
    
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


@route('/getfilters/<queryid>/<loopid>')
def getfilters(queryid, loopid):
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']     
	query = mainbox_table.find_one({'_id': queryid})
	filterstring = ""
	selectedfilters = {}
	if(query.has_key('filters')):
		filterstring = query['filters']
		filters = query['filters'].lstrip(",")
		if(filters != ""):
			filters = filters.split(",")
			for filter in filters:
				keyval = filter.split("|")
				if(len(keyval) == 2):
					if(selectedfilters.has_key(keyval[0])):
						selectedfilters[keyval[0]][keyval[1]] = 1
					else:
						filterh = {keyval[1]: 1}
						selectedfilters[keyval[0]] = filterh


	tags = []
	taghash = {}
	facets = []
	facethash = {}
	if(query.has_key('facets')):
		facets = query['facets'].split(",")
		for facet in facets:
			if(query.has_key(facet)):
				keyval = facet.split("|")
				if(facethash.has_key(keyval[0])):
					facethash[keyval[0]][keyval[1]] = query[facet]
				else:
					faceth = {keyval[1]: query[facet]}
					facethash[keyval[0]] = faceth
		print facethash
				
			
	if(query.has_key('tags')):
		tags = query['tags'].split(",")
	
		for tag in tags:
			if(query.has_key(tag)):
				taghash[tag] = query[tag]
	

	return template('getfilters.html', query = query, tags = tags, taghash = taghash, facethash = facethash, loopid = loopid, selectedfilters = selectedfilters, filterstring = filterstring)


@route('/savedeal/<dealid>/<username>')
def savedeal(dealid, username):
	deal_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
	saved_deal_table = pymongo.Connection('localhost', 27017)[DBNAME]['saved_deals']  
	deal = deal_table.find_one({'_id': dealid})
	deal['username'] = username
	saved_deal_table.insert(deal)
	print "Saving|" + username + ":" + dealid
	sys.stdout.flush()
	return "<strong>Saved</strong>"
    
@route('/unsavedeal/<dealid>/<username>')
def unsavedeal(dealid, username):
	saved_deal_table = pymongo.Connection('localhost', 27017)[DBNAME]['saved_deals']  
	
	saved_deal_table.remove({'username': username, '_id': dealid})
	print "Unsaving|" + username + ":" + dealid
	sys.stdout.flush()
	return ""   
    
    
    
@route('/getdeals/<username>/<queryid>/<startnum>/<resultsize>/:filename')
def getdeals(username, queryid, startnum, resultsize, filename):
	savetab = 0
	startnum = int(startnum) - 1
	resultsize = int(resultsize)
	deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
	deals = []
	
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox'] 
	query = mainbox_table.find_one({'_id': queryid})
	
	keyword = query['keyword']
	dollarlimit = int(query['dollar_limit'])
	pricehigh = int(query['price_high'])
	pricelow = int(query['price_low'])
	dayfilter = int(query['dayfilter'])
	t = timedelta(dayfilter + 1)
	print "Getting deals for {" + keyword + ":" + str(dollarlimit) + "}"
	sys.stdout.flush()
   
	dealquery = { '$and': [{'keyword': keyword}, {'price': {'$lt': pricehigh}}, {'price': {'$gt': pricelow}}, {'founddate': {'$gt':  datetime.utcnow() - t} }] }
    
	filterhash = {}
	if(query.has_key('filters')):
		for filter in query['filters'].split(","):
			keyval = filter.split("|")
			if(len(keyval) == 2):
				if(keyval[0] != 'tag'):
					if(filterhash.has_key(keyval[0])):
						filterhash[keyval[0]][keyval[1]] = 1
					else:
						filterhash[keyval[0]] = {keyval[1]: 1}
				else:
					regx = re.compile(keyval[1],re.IGNORECASE)
					dealquery['$and'].append({'title': {'$regex': regx}})
    
	filterkeys = []
	for filterkey in filterhash.keys():	
		addhash = {'$or': []}
		for filterval in filterhash[filterkey].keys():
			addhash['$or'].append({filterkey: filterval})
		dealquery['$and'].append(addhash)
    
	print dealquery
	deals.extend([deal for deal in deals_table.find(dealquery).sort("founddate", pymongo.DESCENDING).skip(startnum).limit(resultsize)])
    
	saved_deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['saved_deals']
	saved_deals = []
	saved_deals.extend([saved_deal for saved_deal in saved_deals_table.find({'keyword': keyword, 'username': username})])
	sdealhash = {}
	for saved_deal in saved_deals:
		sdealhash[saved_deal['_id']] = 1
    	
	i = 0
	for deal in deals:
		d2 = deal['founddate']
		days = (datetime.utcnow() - d2).days
		deals[i]['days'] = days
		if(sdealhash.has_key(deal['_id'])):
			deals[i]['saved'] = 1
		else:
			deals[i]['saved'] = 0
		i = i + 1
	sys.stdout.flush()
	return template(filename, keyword = keyword, dollarlimit = dollarlimit, deals = deals, username = username, savetab = savetab)
    
@route('/getsaveddeals/<username>/<keyword>/<dollarlimit>')
def getsaveddeals(username, keyword, dollarlimit):
	
	if(keyword == '-1'): 
		mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
		query = mainbox_table.find_one({'username': username})
		keyword = query['keyword']
		dollarlimit = query['dollar_limit']
   
	dollarlimit = int(dollarlimit)
	saved_deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['saved_deals']
	deals = []
	savetab = 1
    
	deals.extend([deal for deal in saved_deals_table.find({'username': username, 'keyword': keyword})])
	i = 0
	for deal in deals:
		d2 = deal['founddate']
		days = (datetime.utcnow() - d2).days
		deals[i]['days'] = days
		deals[i]['saved'] = 2
		i = i + 1
	return template('getdeals.html', keyword = keyword, dollarlimit = dollarlimit, deals = deals, username = username, savetab = savetab)
    
@route('/getqueries/<username>/<linkno>')
def getqueries(username, linkno):
	source = {'id': 1, 'trname': 'trquery', 'linkname': 'query'}
	linkno = int(linkno)
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
	queries = [query for query in mainbox_table.find({'username': username}).sort("lastmodified", pymongo.ASCENDING)]  
	qlen = len(queries)  
	return template('getqueries.html', username = username, linkno = linkno, queries = queries, qlen = qlen, source = source)

@route('/getpopularqueries/<username>/<linkno>')
def getpopularqueries(username, linkno):
	source = {'id': 2, 'trname': 'trpopquery', 'linkname': 'popquery'}
	linkno = int(linkno)
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']    
	queries = [query for query in mainbox_table.find({'username': {'$ne': username}}).limit(6)]  
	qlen = len(queries)  
	return template('getqueries.html', username = username, linkno = linkno, queries = queries, qlen = qlen, source = source)
    

@route('/removequery/<queryid>')
def removequery(queryid):
    
    mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
    #did = bson.objectid.ObjectId(qid)
    
    mainbox_table.remove({'_id': queryid})
    print "Removing| queryid:" + queryid
    sys.stdout.flush()
    return {'status': 'ok'}
