import sys
sys.path.append('./backend/feeds')
import feedslib
import json


configfile = sys.argv[1]
feedsource = sys.argv[2]
keyword = sys.argv[3]
pricelow = sys.argv[4]
pricehigh = sys.argv[5]
maxresults = sys.argv[6]

print "feedsource: " + feedsource
print "keyword: " + keyword
print "pricerange: " + pricelow + " - " + pricehigh
print "maxresults: " + maxresults
print "----------------------------------------------"

f = open(configfile, 'r')
jsonconfig = json.loads(f.read())
print jsonconfig

deals = feedslib.getFeedDeals(feedsource, jsonconfig, keyword, pricehigh, pricelow, maxresults)

ct = 1
for deal in deals:
	print "Result " + str(ct) + ":"
	for key in deal.keys():
		print "\t" + key + " : " + str(deal[key])
	print "----------------------------------------------"
	ct = ct + 1
print "Total result: " + str(len(deals))
