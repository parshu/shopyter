import sys
sys.path.append('./backend/feeds')
import feedslib
import json
import feedsconfig

feedsource = sys.argv[1]
keyword = sys.argv[2]
pricelow = sys.argv[3]
pricehigh = sys.argv[4]
maxresults = sys.argv[5]
zip = sys.argv[6]
city = sys.argv[7]
state = sys.argv[8]

print "feedsource: " + feedsource
print "keyword: " + keyword
print "pricerange: " + pricelow + " - " + pricehigh
print "maxresults: " + maxresults
print "zip: " + zip
print "city: " + city
print "state: " + state
print "----------------------------------------------"


jsonconfig = feedsconfig.CONFIG
print jsonconfig


results = feedslib.getFeedDeals(feedsource, jsonconfig, keyword, pricehigh, pricelow, maxresults, zip, city, state)
deals = results['deals']

ct = 1
for deal in deals:
	print "Result " + str(ct) + ":"
	for key in deal.keys():
		print "\t" + key + " : " + str(deal[key])
	print "----------------------------------------------"
	ct = ct + 1
print "Total result: " + str(len(deals))
print "Tagcloud: " + str(results['tagcloud'])
tagcloud1 = results['tagcloud']
tagcloud2 = results['tagcloud']
mtagcloud = feedslib.consolidateTagClouds([tagcloud1, tagcloud2])
print feedslib.getSortedTagCloudList(mtagcloud)
