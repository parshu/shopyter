
import pymongo
import urllib
import urllib2
import sys
import json
from BeautifulSoup import BeautifulSoup
import unicodedata

def getCLJson(keyword,pricehigh,pricelow,pageindex,zipcode,city,state,DBNAME):
	print "here 91"
	sys.stdout.flush()
	keyword = urllib.quote(keyword)
	cl_table = pymongo.Connection('localhost', 27017)[DBNAME]['clmapping']
	pageindex = str(int(pageindex) * 100)
	if not cl_table.find_one({'_id': zipcode}):
		newzip = int(zipcode) - 1
		if not cl_table.find_one({'_id': str(newzip)}):
			return {'status': 'error: mapping not found for ' + zipcode}
		else:
			zipcode = str(newzip)
	clmapping = cl_table.find_one({'_id': zipcode})
	url = clmapping['baseurl'] + "search/sss?sort=rel&hasPic=1&maxAsk=%s&minAsk=%s&query=%s&srchType=T&s=%s"
	
	url = url %(pricehigh,pricelow,keyword,pageindex)
	print url
   	sys.stdout.flush()
	
	page = urllib2.urlopen(url)
	
	soup = BeautifulSoup(page.read())
	htmljson = {"selfLink": url, "nextLink": "", "totalItems": -1, "startIndex": 1, "itemsPerPage": 100, "currentItemCount": -1, "id": "craigslist.com", "items": []}
	jsonitems = []
	items = soup.findAll('p')

	for item in items:
		jsonitem = {}
		spans = item.findAll('span')
		for span in spans:

			if((span['class'] != None) and ((span.string != None) or (len(span.findAll('font')) > 0))):
				classval = unicodedata.normalize('NFKD', span['class']).encode('ascii','ignore')
				classstr = None
				if(span.string != None):
					classstr = unicodedata.normalize('NFKD', span.string).encode('ascii','ignore')

				name = None
				val = None
				if(classval == "ih"):
					
					
					if(span.has_key('id')):
						name = "image"
						val = "http://images.craigslist.org/" + unicodedata.normalize('NFKD', span['id']).encode('ascii','ignore').replace("images:","")
					
				elif(classval == "itempp"):
					name = "price"
					val = classstr.strip().replace("$","")
					val = float(val)
				elif(classval == "itempn"):
					name = "city"
					locval = None
					for font in span.findAll('font'):
						locval = unicodedata.normalize('NFKD', font.string).encode('ascii','ignore').split("/")[0].strip().replace("(","").replace(")","")
						jsonitem['state'] = state
						break
					if(locval == None):
						locval = classstr.split("/")[0].strip().replace("(","").replace(")","")
						jsonitem['state'] = state
					val = locval
				elif(classval == "itemdate"):
					name = "posteddate"
					val = classstr.strip()
				
				if(name != None):
					jsonitem[name] = val
		atags = item.findAll('a')
		for atag in atags:
			jsonitem['url'] = unicodedata.normalize('NFKD', atag['href']).encode('ascii','ignore')
			jsonitem['title'] = unicodedata.normalize('NFKD', atag.string).encode('ascii','ignore')
			
			break
		
		jsonitems.append(jsonitem)
	
	htmljson['items'] = jsonitems
	return htmljson
