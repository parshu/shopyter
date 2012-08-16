import os
import sys
sys.path.insert(0, os.getcwd())

from collections import defaultdict
import requests

import pymongo
DBNAME = "test"
SERVER = "http://localhost:8080"

from tools.mailer import mail

if __name__ == '__main__':

    deal_url_template = SERVER + '/getemaildeals/%s/1/4/value/descending/emaildeals/getdeals.html'

    users = pymongo.Connection('localhost', 27017)[DBNAME]['users']
    
    for user in users.find():
    	query = deal_url_template % (user['username'])
    	email_text = requests.get(query).text.strip()
        subject = 'Today\'s deals from Shopyter'
        if(email_text != ""):
        	mail(user['email'], subject, email_text)
