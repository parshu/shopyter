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
sys.path.append('./batch')
import deals_updater
from datetime import timedelta
TEMPLATE_PATH.append('./templates')

DBNAME = "test"
PRICE_HIGH_PER = 0.15
PRICE_LOW_PER = 0.25
PRICE_MAX_PER = 2
PRICE_MIN_PER = 2
DEFAULT_DAYS_FILTER = 7
FILTER_ON_LEFT = 1

def getQueryFilters(query):
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
	return({"filterstring": filterstring, "selectedfilters": selectedfilters})

def getQueryFacets(query):
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
	return({"facets": facets, "facethash": facethash})

def getQueryTags(query):
	tags = []
	taghash = {}
	
				
			
	if(query.has_key('tags')):
		tags = query['tags'].split(",")
	
		for tag in tags:
			if(query.has_key(tag)):
				taghash[tag] = query[tag]
	
	return({"tags": tags, "taghash": taghash})
	

def getDealQuery(query):
	keyword = query['keyword']
	dollarlimit = int(query['dollar_limit'])
	pricehigh = int(query['price_high'])
	pricelow = int(query['price_low'])
	dayfilter = int(query['dayfilter'])
	t = timedelta(dayfilter + 1)
	print "Getting deals for {" + keyword + ":" + str(dollarlimit) + "}"
	sys.stdout.flush()
   
	dealquery = { '$and': [{'keyword': keyword}, {'price': {'$lte': pricehigh}}, {'price': {'$gte': pricelow}}, {'founddate': {'$gt':  datetime.utcnow() - t} }] }
    
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
					print "*** %s ***" % (keyval[1])
					regx = re.compile(keyval[1],re.IGNORECASE)
					print regx
					sys.stdout.flush()
					dealquery['$and'].append({'title': {'$regex': regx}})
    
	filterkeys = []
	for filterkey in filterhash.keys():	
		addhash = {'$or': []}
		for filterval in filterhash[filterkey].keys():
			addhash['$or'].append({filterkey: filterval})
		dealquery['$and'].append(addhash)
	
	return(dealquery)

	
@route('/js/:filename')
def serve_jquery_ui_1(filename):
	return static_file(filename, root='./js/')

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


@route('/updatedeallocation/<dealid>/<lat>/<long>')
def updatedeallocation(dealid, lat, long):
	deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
	deal = deals_table.find_one({'_id': dealid})
	deal['lat'] = float(lat)
	deal['long'] = float(long)
	
	deals_table.update({'_id': dealid}, deal)


@route('/updatelocation/<username>/<city>/<state>/<lat>/<long>')
def updatelocation(username, city, state, lat, long):
	users_table = pymongo.Connection('localhost', 27017)[DBNAME]['users']
	userinfo = users_table.find_one({'username': username})
	userinfo['city'] = city
	userinfo['state'] = state
	userinfo['lat'] = float(lat)
	userinfo['long'] = float(long)
	userinfo['zip'] = feedslib.getZipCode(lat, long)
	userinfo['haslocation'] = 1
	users_table.update({'username': username}, userinfo)	
	

@route('/dealsupdate/<username>/<qid>')
def dealsupdate(username, qid):

	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
	query = mainbox_table.find_one({'_id': qid})
	deals_updater.updateQuery(query, mainbox_table, DBNAME)

	lastviewed = query['lastviewed']
	dealquery = getDealQuery(query)

	dealquery['$and'].append({'founddate': {'$gt':  lastviewed} })
	deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
	sys.stdout.flush()
	dealcount = deals_table.find(dealquery).count()
	print "Found additional %s deals..." % (dealcount)

	retstr = "<div></div>"
	
	if(dealcount > 0):
		retstr = "<div class=\"alert alert-block alert-error fade in\" style=\"margin-left:0px;min-height:10px;padding-bottom:5px;padding-top:5px;margin-bottom:5px;margin-left:10px;margin-right:10px;\">We just found " + str(dealcount) + " more new results. <a href=\"#\" onclick=\"clickCurrentQuery();\">Click to see</a></div>"

	return retstr

	
	
@route('/updatemetrics/<username>/<mode>/<metrics>')
def updatemetrics(username, mode, metrics):
	print "Metrics: " + metrics
	sys.stdout.flush()
	metricshash = json.loads(metrics)
	print metricshash
	sys.stdout.flush()
	user_metrics_table = pymongo.Connection('localhost', 27017)[DBNAME]['user_metrics']
	user_metrics = user_metrics_table.find_one({'username': username})
	if not user_metrics:
		metricshash['_id'] = username
		metricshash['username'] = username
		user_metrics_table.insert(metricshash)
	else:
		for key in metricshash.keys():
			if(user_metrics.has_key(key)):
				if(mode == "replace"):
					user_metrics[key] = metricshash[key]
				elif(mode == "increment"):
					if((type(metricshash[key]) is not int) or (type(user_metrics[key]) is not int)):
						print "Could not increment, type not int:" + str(type(metricshash[key])) + str(type(user_metrics[key]))
						sys.stdout.flush()
						return {'status': 'fail', 'error': 'can only increment ints'}
					user_metrics[key] = user_metrics[key] + metricshash[key]
				else:
					print "unknown mode" + mode
					sys.stdout.flush()
					return {'status': 'fail', 'error': 'unknown mode (' + mode + ')'}
			else:
				user_metrics[key] = metricshash[key]
		
		user_metrics_table.update({'_id': username}, user_metrics)
	return {'status': 'ok'}

@route('/:username')
def user(username):
    
	users_table = pymongo.Connection('localhost', 27017)[DBNAME]['users']
	userinfo = users_table.find_one({'username': username})
	if not userinfo:
		return 'User %s not a part of our beta test. Please wait for your invite :-)' % username

	return_user = 1	
    
	if((not userinfo.has_key('return_user')) or (userinfo.has_key('return_user') and (userinfo['return_user'] == 0))):
		userinfo['return_user'] = 1
		users_table.update({'username': username}, userinfo)
		return_user = 0
	
		   
	response.set_cookie('username', username, path = '/')    
    
	return template('userhome.html', username = username, userinfo = userinfo, PRICE_HIGH_PER = PRICE_HIGH_PER, PRICE_LOW_PER = PRICE_LOW_PER, PRICE_MAX_PER = PRICE_MAX_PER, PRICE_MIN_PER = PRICE_MIN_PER, DEFAULT_DAYS_FILTER = DEFAULT_DAYS_FILTER, return_user = return_user, FILTER_ON_LEFT = FILTER_ON_LEFT)



@route('/updatequerypricerange/<qid>/<pricelow>/<pricehigh>')
def updatequerypricerange(qid, pricelow, pricehigh):
	pricelow = int(pricelow)
	pricehigh = int(pricehigh)
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']
	username = request.cookies.get('username')
	print "updating " + qid + ": " + str(pricelow) + " - " + str(pricehigh)
	sys.stdout.flush()
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "price_low" : pricelow , "price_high" : pricehigh, "lastmodified": datetime.utcnow() } })
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
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "dayfilter" : days, "lastmodified": datetime.utcnow() } })
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
	res = mainbox_table.update({'_id': qid, 'username': username}, { "$set" : { "filters" : filters, "lastmodified": datetime.utcnow() } })
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
	currdatetime = datetime.utcnow()
	if(len(querymatches) == 0):
		users_table = pymongo.Connection('localhost', 27017)[DBNAME]['users']
		userinfo = users_table.find_one({'username': username})
		
		inserthash = {'_id': queryhash, 'qid': uniqqueryhash, 'username': username, 'keyword': keyword, 'dollar_limit': dollar, 'price_high': pricehigh, 'price_low': pricelow, 'lastmodified': currdatetime, 'created': currdatetime, 'dayfilter': DEFAULT_DAYS_FILTER, 'pricemax': pricemax, 'pricemin': pricemin, 'city': userinfo['city'], 'state': userinfo['state'], 'zip': userinfo['zip'], 'lat': userinfo['lat'], 'long': userinfo['long']}
		
		results1 = feedslib.getFeedDeals("craigslist", feedsconfig.CONFIG, keyword, pricehigh, pricelow, "",userinfo['zip'],userinfo['city'],userinfo['state'])
		deals1 = results1['deals']
		print "feed1 deals found: " + str(len(deals1))
		results2 = feedslib.getFeedDeals("google", feedsconfig.CONFIG, keyword, pricehigh, pricelow, 25)
		deals2 = results2['deals']
		print "feed2 deals found: " + str(len(deals2))
		results3 = feedslib.getFeedDeals("milo", feedsconfig.CONFIG, keyword, int(pricehigh * 100), int(pricelow * 100), 30, userinfo['zip'])
		deals3 = results3['deals']
		print "feed3 deals found: " + str(len(deals3))
		sys.stdout.flush()
		if(len(deals3) > 0):
			print "Getting merchant info from milo..."
			sys.stdout.flush()
			deals3 = feedslib.updateMiloMerchantInfo(deals3, results3['specialreturn'], userinfo['zip'], 10)
		
		deals = []
		deals.extend(deals1)
		deals.extend(deals2)
		deals.extend(deals3)
		print "Total deals found: " + str(len(deals))
		
		tagcloudlist = [results1['tagcloud'], results2['tagcloud'], results3['tagcloud']]
		mtagcloud = feedslib.consolidateTagClouds(tagcloudlist)
		tagcloud = feedslib.getSortedTagCloudList(mtagcloud)
		tagslist = []
		facetcloudlist = [results1['facetcloud'], results2['facetcloud'], results3['facetcloud']]
		
		
		mfacetcloud = feedslib.consolidateTagClouds(facetcloudlist,4, "channel,condition")
		print "mfacetcloud: " + str(mfacetcloud)
		sys.stdout.flush()
		facetcloud = feedslib.getSortedTagCloudList(mfacetcloud,100)
		print "facetcloud: " + str(facetcloud)
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
			deals_table.insert(deals, continue_on_error=True)
			
			print "Done inserting."
			sys.stdout.flush()
		
		
		print "Inserting query: " + str(inserthash)
		sys.stdout.flush()
		mainbox_table.insert(inserthash)
	else:
		print "Query already exists"
		sys.stdout.flush()
   		
    
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


@route('/savetag/<username>/<queryid>/<tag>')
def savetag(username, queryid, tag):
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']     
	query = mainbox_table.find_one({'_id': queryid})
	if(query.has_key('tags')):
		query['tags'] = query['tags'] + "," + tag
	else:
		query['tags'] = tag
	mainbox_table.update({'_id': queryid, 'username': username}, { "$set" : { "tags" : query['tags'], tag: 0 } })
	return {'status': 'ok'}



@route('/getfilters/<username>/<queryid>/<loopid>')
def getfilters(username, queryid, loopid):
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox']     
	query = mainbox_table.find_one({'_id': queryid})


	filterresults = getQueryFilters(query)
	facetresults = getQueryFacets(query)
	tagresults = getQueryTags(query)
	

	return template('getfilters.html', query = query, tags = tagresults['tags'], taghash = tagresults['taghash'], facethash = facetresults['facethash'], loopid = loopid, selectedfilters = filterresults['selectedfilters'], filterstring = filterresults['filterstring'], username = username)


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
    
    
    
@route('/getdeals/<username>/<queryid>/<startnum>/<resultsize>/<zoom>/:filename')
def getdeals(username, queryid, startnum, resultsize, zoom, filename):
	user_metrics_table = pymongo.Connection('localhost', 27017)[DBNAME]['user_metrics']
	user_metrics = user_metrics_table.find_one({'username': username})
	savetab = 0
	zoom = int(zoom)
	startnum = int(startnum) - 1
	resultsize = int(resultsize)
	deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['deals']
	deals = []
	
	mainbox_table = pymongo.Connection('localhost', 27017)[DBNAME]['mainbox'] 
	query = mainbox_table.find_one({'_id': queryid})
	
	qlastviewed = None
	if(query.has_key('lastviewed')):
		qlastviewed = query['lastviewed']
	
	facetresults = getQueryFacets(query)
	filterresults = getQueryFilters(query)
	
	dealquery = getDealQuery(query)
    
	print dealquery
	deals.extend([deal for deal in deals_table.find(dealquery).sort("founddate", pymongo.DESCENDING).skip(startnum).limit(resultsize)])
    
	saved_deals_table = pymongo.Connection('localhost', 27017)[DBNAME]['saved_deals']
	saved_deals = []
	saved_deals.extend([saved_deal for saved_deal in saved_deals_table.find({'keyword': query['keyword'], 'username': username})])
	sdealhash = {}
	for saved_deal in saved_deals:
		sdealhash[saved_deal['_id']] = 1
    	
    
	updateCountFields = ['channel']	
	addresshash = {}
	i = 0
	fieldhash = {}
	for field in updateCountFields:
		fieldhash[field] = {}
	for deal in deals:
		fulladdress = []
		if(deal.has_key('city')):
			if(deal.has_key('street')):
				fulladdress.append(deal['street'])
			fulladdress.append(deal['city']) 
			if(deal.has_key('state')):
				fulladdress.append(deal['state'])
			if(deal.has_key('zip')):
				fulladdress.append(deal['zip'])
			fulladdress = ','.join(fulladdress)
			if(not addresshash.has_key(fulladdress)):
				addresshash[fulladdress] = []
			addresshash[fulladdress].append(deal)
			
		
		if(qlastviewed != None):
			if(deal['founddate'] > qlastviewed):
				deals[i]['unseen'] = 1
		else:
			deals[i]['unseen'] = 1
			
		d2 = deal['founddate']
		days = (datetime.utcnow() - d2).days
		deals[i]['days'] = days
		if(sdealhash.has_key(deal['_id'])):
			deals[i]['saved'] = 1
		else:
			deals[i]['saved'] = 0
		
		for field in updateCountFields:
			if(deals[i].has_key(field)):
				if(fieldhash[field].has_key(deals[i][field])):
					fieldhash[field][deals[i][field]] = fieldhash[field][deals[i][field]] + 1
				else:
					fieldhash[field][deals[i][field]] = 1
		i = i + 1
	sys.stdout.flush()
	facethash = facetresults['facethash']
	
	
	for field in updateCountFields:
		if(facethash.has_key(field)):
			for f in facethash[field].keys():
				if(fieldhash[field].has_key(f)):
					facethash[field][f] = fieldhash[field][f]
				else:
					if(facethash[field].has_key(f)):
						facethash[field][f] = 0
	
	spans = 0
	if(facethash.has_key('channel')):
		spans = spans + len(facethash['channel'].keys())
	spans = int(12/spans)
	
	mainbox_table.update({'_id': query["_id"], 'username': username}, { "$set" : { "lastviewed": datetime.utcnow() } })
	
	return template(filename, keyword = query['keyword'], dollarlimit = int(query['dollar_limit']), deals = deals, username = username, savetab = savetab, user_metrics = user_metrics, query = query, facethash = facethash, spans = spans, selectedfilters = filterresults['selectedfilters'], addresshash = addresshash, zoom = zoom)
    
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
	queries = [query for query in mainbox_table.find({'username': username}).sort("created", pymongo.ASCENDING)]  
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
