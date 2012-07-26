
import urllib2
import json
import urllib
import sys
import os
import datetime
import hashlib
import unicodedata
import re
from operator import itemgetter
import itertools

def gethash(s):
	h = hashlib.new('ripemd160')
	h.update(s)
	return(h.hexdigest())
	
def consolidateTagClouds(tagcloudlist, threshold=7):
	if(len(tagcloudlist) == 0):
		return None
	resulttagcloud = tagcloudlist[0]
	
		
	
	for tagcloud in tagcloudlist[1:len(tagcloudlist)]:
		for key in tagcloud.keys():
			if(resulttagcloud.has_key(key)):
				resulttagcloud[key] = resulttagcloud[key] + tagcloud[key]
			else:
				resulttagcloud[key] = tagcloud[key]
			if(resulttagcloud[key] < threshold):
				del resulttagcloud[key]
	
	for key in resulttagcloud.keys():
		if(resulttagcloud[key] < threshold):
				del resulttagcloud[key]
	return resulttagcloud

def getSortedTagCloudList(tagcloud, cutoff=8):
	
	tagcloudlist = sorted(tagcloud.items(), key=itemgetter(1), reverse=True)
	
	tagslice = cutoff
	if(len(tagcloudlist) < tagslice):
		tagslice = len(tagcloudlist)
	tagcloudlist = tagcloudlist[0:tagslice]
	return tagcloudlist


def getFeedDeals(feedsource, jsonconfig, keyword, pricehigh, pricelow, maxresults, zipcode="", city="", state=""):
	
	feedconfig = None
	deals = []
	for fconfig in jsonconfig['feeds']:
		if(fconfig['feedsource'] == feedsource):
			 feedconfig = fconfig
			 break
	if(feedconfig == None):
		raise Exception("Error: Feed configurations not found. Check \"feedsource\" field and make sure it exists.")
	keywordtags = re.split('\W+', keyword.title())	 
	keyword = urllib.quote(keyword)
	pricehigh = str(pricehigh)
	pricelow = str(pricelow)
	maxresults = str(maxresults)
	city = urllib.quote(city)
	
	print [keyword, maxresults, pricelow, pricehigh, zipcode, city, state]
	
	url = feedconfig['feedurl']
	feedtags = feedconfig['feedtagfields'].split(",")
	feedfacets = feedconfig['feedfacetfields'].split(",")
	
	if(feedconfig.has_key('feedkeyname')):
		url = url + feedconfig['feedkeyname'] + "=" + feedconfig['feedkeyvalue'] + "&"
	
	url = url  + feedconfig['feedparams'] % (keyword, maxresults, pricelow, pricehigh, zipcode, city, state)
	print url
	
	try:
		request = urllib2.Request(url)
		request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
		response = urllib2.urlopen(request, timeout=2)
	except urllib2.HTTPError, e:
		print "Ecode:" + str(e.code)
	except urllib2.URLError, e:
		print "Eargs:" + str(e.args)
	
	tagcloud = {}
	facetcloud = {}
	
	
	results = json.loads(response.read())	
	dataitems = feedconfig['feeddatatostore']
	
	for result in results[feedconfig['resultslistfield']]:
		dealresult = {}
		for datakey in dataitems.keys():
			val = result
			for datavals in dataitems[datakey].split(','):
				if(datavals[0] == '#'):
					val = datavals.replace("#","")
					break
				if(datavals.isdigit()):
					val = val[int(datavals)]
				else:
					if(val.has_key(datavals)):
						val = val[datavals]
					else:
						continue
						
			if( (type(val) is dict) or (type(val) is list)):
				pass 
			else:
				dealresult[datakey] = val
				if(datakey in feedfacets):
					datakeyascii = datakey
					valascii = val
					
					facetkey = datakeyascii + "|" + valascii
					
					if(facetcloud.has_key(facetkey)):
						facetcloud[facetkey] = facetcloud[facetkey] + 1
					else:
						facetcloud[facetkey] = 1
							
				if(datakey in feedtags):
					valascii = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
					tags = re.split('\W+', valascii)
					for tag in tags:
						if(tag.isdigit() or tag.islower() or (tag == '') or (tag in keywordtags)):
							continue
						
						tag = tag.title()
						if(tagcloud.has_key(tag)):
							tagcloud[tag] = tagcloud[tag] + 1
						else:
							tagcloud[tag] = 1
		dealresult['keyword'] = urllib.unquote(keyword)
		dealresult['founddate'] = datetime.datetime.utcnow()
		hashstr = ""
		for component in jsonconfig['hashcomponents']:
			if(dealresult.has_key(component)):
				if((type(dealresult[component]) is int) or (type(dealresult[component]) is float)):
					hashstr = hashstr + str(dealresult[component])
				else:
					hashstr = hashstr + dealresult[component]
							
		hashstr = unicodedata.normalize('NFKD', hashstr).encode('ascii','ignore')
		dealresult["_id"] = gethash(hashstr)
		deals.append(dealresult)
	
	
	return({'deals': deals, 'tagcloud': tagcloud, 'facetcloud': facetcloud})