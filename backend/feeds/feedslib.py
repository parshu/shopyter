import time
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


def updateMiloMerchantInfo(deals, merchantinfo, zip, radius):
	
	midstr = ','.join(merchantinfo['merchantid'])
	fields = ['city', 'store_id', 'region', 'longitude', 'phone', 'street', 'postal_code', 'latitude']
	url = "https://api.x.com/milo/v3/store_addresses?key=6962be92d8a82bb760d7081c15e1ea7f&merchant_ids=%s&postal_code=%s&radius=%s&show=DescSidMidHoursLocMlogo" % (midstr, zip, radius)
	
	print url
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
	response = urllib2.urlopen(request, timeout=2)
	resp = response.read()
	results = json.loads(resp)
	storeinfo = {}
	for store in results['store_addresses']:
		if(not storeinfo.has_key(store['merchant_id'])):
			storeinfo[store['merchant_id']] = []
		storeinfo[store['merchant_id']].append(store)

	for deal in deals:
		if(storeinfo.has_key(deal['merchantid'])):
			deal['source'] = storeinfo[deal['merchantid']][0]['merchant_name'].replace("\""," ")
			deal['street'] = storeinfo[deal['merchantid']][0]['street']
			deal['city'] = storeinfo[deal['merchantid']][0]['city']
			deal['state'] = storeinfo[deal['merchantid']][0]['region']
			deal['zip'] = storeinfo[deal['merchantid']][0]['postal_code']
			deal['long'] = storeinfo[deal['merchantid']][0]['longitude']
			deal['lat'] = storeinfo[deal['merchantid']][0]['latitude']
			deal['storeid'] = storeinfo[deal['merchantid']][0]['store_id']
			 	
	return deals


def getZipCode(lat, long):
	url = "http://www.geoplugin.net/extras/postalcode.gp?lat=%s&long=%s&format=json" % (lat, long)
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
	response = urllib2.urlopen(request, timeout=2)
	resp = response.read()
	resp = resp.replace("geoPlugin(","")
	resp = resp.replace(")","")
	results = json.loads(resp)
	return results['geoplugin_postCode']
	

def gethash(s):
	h = hashlib.new('ripemd160')
	h.update(s)
	return(h.hexdigest())
	
def consolidateTagClouds(tagcloudlist, threshold=7, exceptkeys=""):
	exceptlist = exceptkeys.split(",")
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
				keytemp = key.split("|")[0]
				if(not keytemp in exceptlist):
					del resulttagcloud[key]
	
	for key in resulttagcloud.keys():
		keytemp = key.split("|")[0]
		if(resulttagcloud[key] < threshold):
			if(not keytemp in exceptlist):
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
	specialReturn = {}
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
		response = urllib2.urlopen(request, timeout=10)
	except urllib2.HTTPError, e:
		print "Ecode:" + str(e.code)
	except urllib2.URLError, e:
		print "Eargs:" + str(e.args)
	
	tagcloud = {}
	facetcloud = {}
	
	resp = response.read()
	results = json.loads(resp)	
	dataitems = feedconfig['feeddatatostore']
	
	if(feedconfig.has_key('additionallistreturn')):
		specialReturn[feedconfig['additionallistreturn']] = []
	
	if(not results.has_key(feedconfig['resultslistfield'])):
		return({'deals': deals, 'tagcloud': tagcloud, 'facetcloud': facetcloud})
		
	
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
					iscents = False
					if(datavals.find("(c)") == 0):
						datavals = datavals.replace("(c)", "")
						iscents = True
						
					if(val.has_key(datavals)):
						val = val[datavals]
						if(iscents):
							val = val/100.0
					else:
						continue
						
			if( (val == None) or (type(val) is dict) or (type(val) is list)):
				pass 
			else:
				if(type(val) == unicode):
					val = unicodedata.normalize('NFKD', val).encode('ascii','ignore')
				dealresult[datakey] = val
				if(feedconfig.has_key('additionallistreturn')):
					if(datakey == feedconfig['additionallistreturn']):
						valstr = str(val)
						if(not valstr in specialReturn[feedconfig['additionallistreturn']]):
							specialReturn[feedconfig['additionallistreturn']].append(valstr)
				
				if(datakey in feedfacets):
					datakeyascii = datakey
					if(val.find(".") >= 0):
						val = val.replace(".","")
						dealresult[datakey] = val
					valascii = val
					
					facetkey = datakeyascii + "|" + valascii
					
					
					if(facetcloud.has_key(facetkey)):
						facetcloud[facetkey] = facetcloud[facetkey] + 1
					else:
						facetcloud[facetkey] = 1
				
							
				if(datakey in feedtags):
					valascii = val
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
							
		
		dealresult["_id"] = gethash(hashstr)
		deals.append(dealresult)
	
	
	return({'deals': deals, 'tagcloud': tagcloud, 'facetcloud': facetcloud, 'specialreturn': specialReturn})