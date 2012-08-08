import os
import sys
sys.path.insert(0, os.getcwd())
import pymongo
import urllib
import urllib2
sys.path.append('./backend/feeds')
sys.path.append('./backend/feeds/feedconvertors/craigslist')
import feedslib
import feedsconfig
import json
from BeautifulSoup import BeautifulSoup
import unicodedata
import CLJsonFeed
import datetime


def updateQuery(query, mainbox_table, db):
	
	keywords = []
	keywords.append(query['keyword'])
	filters = []
	if(query.has_key('filters')):
		filters = query['filters'].lstrip(",").split(",")
	
	for filter in filters:
		keyval = filter.split("|")
		if(len(keyval) == 2):
			if(keyval[0] != "channel"):
				keywords.append(keyval[1])
			
	keyword = " ".join(keywords)
	pricehigh = int(query["price_high"] + (query["price_high"] * 0.10))
	pricelow = int(query["price_low"] - (query["price_low"] * 0.10))
	zip = query['zip']
	city = query['city']
	state = query['state']
	print "Updating deals for (%s): keyword(%s), pricehigh(%s), pricelow(%s) @%s, %s %s" % (query['_id'], keyword, pricehigh, pricelow, city, state, zip)
	
	results1 = feedslib.getFeedDeals("craigslist", feedsconfig.CONFIG, keyword, pricehigh, pricelow, "",zip,city,state)
	deals1 = results1['deals']
	print "feed1 deals found: " + str(len(deals1))
	results2 = feedslib.getFeedDeals("google", feedsconfig.CONFIG, keyword, pricehigh, pricelow, 25)
	deals2 = results2['deals']
	print "feed2 deals found: " + str(len(deals2))
	results3 = feedslib.getFeedDeals("milo", feedsconfig.CONFIG, keyword, int(pricehigh * 100), int(pricelow * 100), 30, zip)
	deals3 = results3['deals']
	if(len(deals3) > 0):
		deals3 = feedslib.updateMiloMerchantInfo(deals3, results3['specialreturn'], zip, 10)
	print "feed3 deals found: " + str(len(deals3))
	sys.stdout.flush()
	deals = []
	deals.extend(deals1)
	deals.extend(deals2)
	deals.extend(deals3)
	for deal in deals:
		deal['keyword'] = query['keyword']
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
		if(query.has_key(tag[0])):
			query[tag[0]] = query[tag[0]] + tag[1]
		else:
			query[tag[0]] = tag[1]
		tagslist.append(tag[0])

	querytaglist = query["tags"].split(",")
	for tag in tagslist:
		if(not tag in querytaglist):
			querytaglist.append(tag)
			
	query["tags"] = ','.join(querytaglist)


	for facet in facetcloud:
		
		if(query.has_key(facet[0])):
			query[facet[0]] = query[facet[0]] + facet[1]
		else:
			query[facet[0]] = facet[1]
		facetslist.append(facet[0])
	
	queryfacetlist = query["facets"].split(",")
	for facet in facetslist:
		if(not facet in queryfacetlist):
			queryfacetlist.append(facet)
			
	query["facets"] = ','.join(queryfacetlist)
	query["lastmodified"] = datetime.datetime.utcnow()
	mainbox_table.update({'_id': query['_id']}, query)
	sys.stdout.flush()
	if(len(deals) > 0):
		deals_table = pymongo.Connection('localhost', 27017)[db]['deals']
		print "Inserting into deals table..."
		sys.stdout.flush()
		deals_table.insert(deals, continue_on_error=True)
				
		print "Done inserting."
		sys.stdout.flush()


if __name__ == '__main__':

	db = sys.argv[1]
	
	
	users_table = pymongo.Connection('localhost', 27017)[db]['users']
	mainbox_table = pymongo.Connection('localhost', 27017)[db]['mainbox']
	
	users = users_table.find()
	for user in users:
		print "Updating deals for [%s]..." % (user['username'])
		queries = mainbox_table.find()
		for query in queries:
			updateQuery(query, mainbox_table, db)
			#print "Error: Something went wrong in updating \"" + query['_id'] + "\",\"" + query['keyword'] + "\" for \"" + user['username'] + "\""
	
	