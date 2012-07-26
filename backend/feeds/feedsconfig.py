
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
			"feedsource": "craigslist",
			"feedurl": "",
			"feedparams": "http://localhost:8079/getclfeed/%s%s/%s/%s/0/%s/%s/%s",
			"feedreplacementfields": "keyword, maxresults, pricehigh, pricelow, zipcode, city, state",
			"feedtagfields":"title",
			"feedfacetfields":"condition,channel,source,city",
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
        		
        			
        				