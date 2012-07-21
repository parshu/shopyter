
CONFIG = {
	"dbname": "test",
	"dealstablename": "deals",
	"producttablename" : "product",
	"feeds" : [
		{
			"feedsource": "google",
			"feedurl": "https://www.googleapis.com/shopping/search/v1/public/products?",
			"feedkeyname": "key",
			"feedkeyvalue": "AIzaSyAH7frOOslC7tXHdC-WiJ16d4uhsI_1PQY",
			"feedparams": "&country=US&q=%s&max-results=%s&restrictBy=price=[%s,%s]",
			"feedreplacementfields": "keyword, pricelow, pricehigh",
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
		}
	]
}
        		
        			
        				