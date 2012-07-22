import urllib2
import json
import urllib
import sys
import os
import datetime
import hashlib
import unicodedata

def gethash(s):
	h = hashlib.new('ripemd160')
	h.update(s)
	return(h.hexdigest())


def getFeedDeals(feedsource, jsonconfig, keyword, pricehigh, pricelow, maxresults):
	feedconfig = None
	deals = []
	for fconfig in jsonconfig['feeds']:
		if(fconfig['feedsource'] == feedsource):
			 feedconfig = fconfig
			 break
	if(feedconfig == None):
		raise Exception("Error: Feed configurations not found. Check \"feedsource\" field and make sure it exists.")
	
			 
	keyword = urllib.quote(keyword)
	pricehigh = str(pricehigh)
	pricelow = str(pricelow)
	maxresults = str(maxresults)
	
	url = feedconfig['feedurl'] + feedconfig['feedkeyname'] + "=" + feedconfig['feedkeyvalue'] + "&" + feedconfig['feedparams'] %(keyword, maxresults, pricelow, pricehigh)
	
	response = urllib2.urlopen(url)
	results = json.loads(response.read())	
	dataitems = feedconfig['feeddatatostore']
	for result in results[feedconfig['resultslistfield']]:
		dealresult = {}
		for datakey in dataitems.keys():
			val = result
			for datavals in dataitems[datakey].split(','):
	
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
		
	return(deals)