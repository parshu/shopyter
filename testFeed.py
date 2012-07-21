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

print "feedsource: " + feedsource
print "keyword: " + keyword
print "pricerange: " + pricelow + " - " + pricehigh
print "maxresults: " + maxresults
print "----------------------------------------------"


jsonconfig = feedsconfig.CONFIG
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
