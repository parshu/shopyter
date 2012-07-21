import urllib2
import json
import urllib
import sys
import os



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
						
				
			dealresult[datakey] = val
		
		deals.append(dealresult)
		
	return(deals)