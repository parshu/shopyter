import urllib2
import json

def updateMiloMerchantInfo(deals, merchantinfo, zip, radius):
	
	midstr = ','.join(merchantinfo['merchantid'])
	fields = ['city', 'store_id', 'region', 'longitude', 'phone', 'street', 'postal_code', 'latitude']
	url = "https://api.x.com/milo/v3/store_addresses?key=6962be92d8a82bb760d7081c15e1ea7f&merchant_ids=%s&postal_code=%s&radius=%s&show=DescSidMidHoursLocMlogo" % (midstr, zip, radius)
	
	print url
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/6.0 (Macintosh; I; Intel Mac OS X 11_7_9; de-LI; rv:1.9b4) Gecko/2012010317 Firefox/10.0a4')
	response2 = None
	try:
		response2 = urllib2.urlopen(request, timeout=10)
	except:
		response2 = urllib2.urlopen(request, timeout=10)
	resp = response2.read()
	results = json.loads(resp)
	response2.close()
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