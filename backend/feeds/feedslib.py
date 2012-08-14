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
import math
import milo

STOP_WORDS = {'the': 1, 'for': 1, 'by': 1, 'and': 1}
def getTagCloud(tagcloud, tags, excludelist):
	
	for tag in tags:
		if(tag.isdigit() or tag.islower() or (tag == '') or (tag.title() in excludelist) or (STOP_WORDS.has_key(tag.lower()))):
			continue
		
		tagupper = tag.upper()
		tagtitle = tag.title()
		taglower = tag.lower()
		if(tagcloud.has_key(tagupper)):
			tagcloud[tagupper] = tagcloud[tagupper] + 1
		elif(tagcloud.has_key(tagtitle)):
			if(tag.isupper()):
				tagcloud[tag] = tagcloud[tagtitle] + 1
				del tagcloud[tagtitle]
			else:
				tagcloud[tagtitle] = tagcloud[tagtitle] + 1
		elif(tagcloud.has_key(taglower)):
			if(tag.isupper()):
				tagcloud[tag] = tagcloud[taglower] + 1
				del tagcloud[taglower]
			elif(tag.istitle()):
				tagcloud[tag] = tagcloud[taglower] + 1
				del tagcloud[taglower]
			else:
				tagcloud[taglower] = tagcloud[taglower] + 1
		elif(tagcloud.has_key(tag)):
			tagcloud[tag] = tagcloud[tag] + 1
		else:
			tagcloud[tag] = 1
	return tagcloud

def getBigrams(words):
	bigrams = []
	wprev = None
	for w in words:
		if(STOP_WORDS.has_key(w.lower())):
			wprev = None
			continue
		if(w.isdigit()):
			wprev = w
			continue
		if((w == "") or (w == " ")):
			continue
		if(wprev != None):
			bigrams.append(wprev + " " + w)
		wprev = w
	return bigrams

def getZipCode(lat, long):
	url = "http://www.geoplugin.net/extras/postalcode.gp?lat=%s&long=%s&format=json" % (lat, long)
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
	response = urllib2.urlopen(request, timeout=10)
	resp = response.read()
	resp = resp.replace("geoPlugin(","")
	resp = resp.replace(")","")
	results = json.loads(resp)
	return results['geoplugin_postCode']
	

def gethash(s):
	h = hashlib.new('ripemd160')
	h.update(s)
	return(h.hexdigest())
	
def consolidateTagClouds(tagcloudlist, threshold=7, exceptkeys="", type="tags"):
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
			
	
	for key in resulttagcloud.keys():
		if(resulttagcloud.has_key(key)):
			keytemp = key.split("|")[0]
			if(not keytemp in exceptlist):
				if(resulttagcloud[key] < threshold):
					del resulttagcloud[key]
					continue
				if((resulttagcloud[key] >= 3) and (key.find(" ") > 0)):
					bigram = key.split(" ")
					for gram in bigram:
						if(resulttagcloud.has_key(gram)):
							del resulttagcloud[gram]
				if(type == "tags"):
					if(not (key.istitle() or key.isupper())):
						del resulttagcloud[key]
						continue
				
				
	return resulttagcloud






def getSortedTagCloudList(tagcloud, cutoff=8):
	
	tagcloudlist = sorted(tagcloud.items(), key=itemgetter(1), reverse=True)
	
	tagslice = cutoff
	if(len(tagcloudlist) < tagslice):
		tagslice = len(tagcloudlist)
	tagcloudlist = tagcloudlist[0:tagslice]
	return tagcloudlist


def getFeedDeals(feedsource, jsonconfig, keyword, origkeyword, pricehigh, pricelow, maxresults, zipcode="", city="", state=""):
	
	
	feedconfig = None
	deals = []
	specialReturn = {}
	for fconfig in jsonconfig['feeds']:
		if(fconfig['feedsource'] == feedsource):
			 feedconfig = fconfig
			 break
	if(feedconfig == None):
		raise Exception("Error: Feed configurations not found. Check \"feedsource\" field and make sure it exists.")
	ktitle = keyword.title()
	ktitle = ktitle.replace("'","")
	keywordtags = re.split('\W+', ktitle)	
	keywordbigramtags = getBigrams(keywordtags) 
	keyword = urllib.quote(keyword)
	pricehigh = str(pricehigh)
	pricelow = str(pricelow)
	maxresults = str(maxresults)
	city = urllib.quote(city)
	lowestprice = pricehigh
	print [keyword, maxresults, pricelow, pricehigh, zipcode, city, state]
	
	url = feedconfig['feedurl']
	feedtags = feedconfig['feedtagfields'].split(",")
	feedfacets = feedconfig['feedfacetfields'].split(",")
	
	if(feedconfig.has_key('feedkeyname')):
		url = url + feedconfig['feedkeyname'] + "=" + feedconfig['feedkeyvalue'] + "&"
	
	url = url  + feedconfig['feedparams'] % (keyword, maxresults, pricelow, pricehigh, zipcode, city, state)
	print url
	
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
	response = urllib2.urlopen(request, timeout=10)
	
	
	tagcloud = {}
	facetcloud = {}
	bigramtagcloud = {}
	
	resp = response.read()
	results = json.loads(resp)	
	response.close()
	dataitems = feedconfig['feeddatatostore']
	if(feedconfig.has_key('additionallistreturn')):
		specialReturn[feedconfig['additionallistreturn']] = []
	
	if(not results.has_key(feedconfig['resultslistfield'])):
		return({'deals': deals, 'tagcloud': tagcloud, 'facetcloud': facetcloud})
		
	resultindex = 0
	resultscount = len(results)
	matchstrict = 0
	if((resultscount < 5) and (len(keywordtags) > 1)):
		matchstrict = 0
	for result in results[feedconfig['resultslistfield']]:
		dealresult = {}
		for datakey in dataitems.keys():
			val = result
			for datavals in dataitems[datakey].split(','):
				if(datavals[0] == '#'):
					val = datavals.replace("#","")
					break
				if(datavals.isdigit()):
					
					if((type(val) is list) and (len(val) > int(datavals))):
						val = val[int(datavals)]
					else:
						val = None
						break
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
					valstripped = valascii.replace("'","")
					tags = re.split('\W+', valstripped)
					bigramtags = getBigrams(tags)
					tagcloud = getTagCloud(tagcloud, tags, keywordtags)
					bigramtagcloud = getTagCloud(bigramtagcloud, bigramtags, keywordbigramtags)
		if(not dealresult.has_key('price')):
			continue
		
		if(dealresult.has_key("title")):
			dealtitle = dealresult['title']
			dealresult['thumbnail_title'] = (dealtitle[:34] + '..') if len(dealtitle) > 35 else dealtitle
			dealresult['listing_title'] = (dealtitle[:68] + '..') if len(dealtitle) > 70 else dealtitle
			ki = 0
			for keyt in keywordtags:
				if(dealtitle.find(keyt) >= 0):
					ki = ki + 1
			if(ki < matchstrict):
				print "Failed strictness test. Dropping [%s]" % (str(dealresult))
				continue
		else:
			continue
		dealresult['keyword'] = urllib.unquote(keyword)
		dealresult['founddate'] = datetime.datetime.utcnow()
		dealresult['popularity'] = float(((float(resultscount)/float(resultindex + 1))/float(resultscount)) * 100.0)
		dealresult['popularity_rating'] = int(math.floor(dealresult['popularity'] / 20))
		if(dealresult.has_key('city')):
			dealresult['city'] = dealresult['city'].title()
		if(dealresult.has_key('state')):
			dealresult['state'] = dealresult['state'].upper()
		lowestprice = float(pricelow)
		highestprice = float(pricehigh)
		if(feedconfig['feeddenomination'] == "cents"):
			lowestprice = lowestprice / 100.0
		pricefactor = ((highestprice - dealresult['price'])/highestprice) * 100.0
		harmonicmean = (2 * pricefactor * dealresult['popularity'])/(pricefactor + dealresult['popularity'])
		dealresult['value'] = harmonicmean
		print "pricelow:%s, dealprice:%s, value:%s, popularity:%s" % (lowestprice, dealresult['price'], (float(lowestprice)/dealresult['price']), dealresult['popularity'])
		dealresult['value_rating'] = int(3 + math.floor(dealresult['value'] / 50))
		hashstr = ""
		for component in jsonconfig['hashcomponents']:
			if(dealresult.has_key(component)):
				if((type(dealresult[component]) is int) or (type(dealresult[component]) is float)):
					hashstr = hashstr + str(dealresult[component])
				else:
					hashstr = hashstr + dealresult[component]
							
		hashstr = hashstr + origkeyword
		dealresult["_id"] = gethash(hashstr)
		deals.append(dealresult)
		if(dealresult['price'] < lowestprice):
			lowestprice = dealresult['price']
		resultindex = resultindex + 1
		
	return({'deals': deals, 'tagcloud': dict(tagcloud.items() + bigramtagcloud.items()), 'facetcloud': facetcloud, 'specialreturn': specialReturn, 'lowestprice': lowestprice})