
CONFIG = {
	"dbname": "test",
	"dealstablename": "deals",
	"producttablename" : "product",
	"hashcomponents": [
		"title",
		"source",
		"price",
		"shipping",
		"brand",
		"condition",
		"channel",
		"keyword"		
	],
	"feeds" : [
		{
			"feedsource": "google",
			"feeddenomination":"cents",
			"feedurl": "https://www.googleapis.com/shopping/search/v1/public/products?",
			"feedkeyname": "key",
			"feedkeyvalue": "AIzaSyAH7frOOslC7tXHdC-WiJ16d4uhsI_1PQY",
			"feedparams": "&country=US&q=%s&max-results=%s&restrictBy=price=[%s,%s]%s%s%s",
			"feedreplacementfields": "keyword, maxresults, pricelow, pricehigh, zipcode, city, state",
			"feedtagfields":"title",
			"feedfacetfields":"brand,condition,channel,source",
			"resultscountfield": "currentItemCount",
			"resultslistfield" : "items",
			"feeddatatostore": {	
				"feedresultid" : "product,googleId",
				"title" : "product,title",
				"source" : "product,author,name",
				"sourceid" : "product,author,accountId",
				"modifiedtime" : "product,modificationTime",
				"description" : "product,description",
				"brand" : "product,brand",
				"condition" : "product,condition",
				"channel" : "product,inventories,0,channel",
				"available" : "product,inventories,0,availability",
				"price" : "product,inventories,0,price",
				"shipping" : "product,inventories,0,shipping",
				"url" : "product,link",
				"image" : "product,images,0,link"
			}
			
		},
		{
			"feedsource": "milo",
			"feeddenomination":"cents",
			"additionallistreturn":"merchantid",
			"feedurl": "https://api.x.com/milo/v3/products?",
			"feedkeyname": "key",
			"feedkeyvalue": "6962be92d8a82bb760d7081c15e1ea7f",
			"feedparams": "q=%s&page=0&per_page=%s&min_price=%s&max_price=%s&postal_code=%s&show_defaults=true&show=PidEpidPnamePurlMidsSpecAvscoreAttrsBrandCatnameCattreePmaxPminSaleUpcAsinRateRatecntImg100&sort_by=relevance%s%s",
			"feedreplacementfields": "keyword, maxresults, pricelow, pricehigh, zipcode, city, state",
			"feedtagfields":"name",
			"feedfacetfields":"brand,condition,channel",
			"resultscountfield": "per_page",
			"resultslistfield" : "products",
			"feeddatatostore": {	
				"feedresultid" : "product_id",
				"title" : "name",
				"source" : "#-1",
				"sourceid" : "merchants,0",
				"merchantid" : "merchants,0",
				"brand" : "brand_name",
				"condition" : "#new",
				"channel" : "#in-store",
				"availability_score" : "availability_score",
				"price" : "(c)min_price",
				"url" : "product_url",
				"image" : "image_100"
			}
			
		},
		{
			"feedsource": "craigslist",
			"feeddenomination":"usd",
			"feedurl": "",
			"feedparams": "http://localhost:8079/getclfeed/%s%s/%s/%s/0/%s/%s/%s",
			"feedreplacementfields": "keyword, maxresults, pricehigh, pricelow, zipcode, city, state",
			"feedtagfields":"title",
			"feedfacetfields":"condition,channel,source",
			"feedlocationfields":"city",
			"resultscountfield": "totalItems",
			"resultslistfield" : "items",
			"feeddatatostore": {	
				"title" : "title",
				"source" : "#craigslist",
				"modifiedtime" : "posteddate",
				"condition" : "#used",
				"channel" : "#local",
				"price" : "price",
				"url" : "url",
				"image" : "image",
				"city" : "city",
				"state" : "state"
			}
			
		}
	]
}
        		
        			
        				