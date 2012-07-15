import os
import sys
sys.path.insert(0, os.getcwd())

from collections import defaultdict
import requests

import pymongo

from tools.mailer import mail

if __name__ == '__main__':

    testing = sys.argv[1] == 'testing' if len(sys.argv) == 2 else False
    deal_url_template = 'http://knopon.com/getdealemail/%s/%s/0'

    mainbox = pymongo.Connection('127.0.0.1', 27017)['master']['mainbox']
    users = pymongo.Connection('127.0.0.1', 27017)['master']['users']
    
    user_queries = defaultdict(list)
    if not testing:
        user_emails = dict([(user['username'], user['email']) for user in users.find()])
    else:
        user_emails = dict([(user['username'], 'knopon@gmail.com') for user in users.find()])

    for query in mainbox.find():
        user_queries[query['username']].append(deal_url_template % (query['keyword'], str(query['dollar_limit'])))
        
    for user, queries in user_queries.iteritems():
        email_text = '<html><body><h3>We have some amazing new deals for you today. Click here to manage your deals - <a href="http://knopon.com/' + user + '">http://knopon.com/' + user + '</a></h3><hr>'
        for query in queries:
            email_text += requests.get(query + "/" + user).text.strip()
            email_text += '<hr/>'
        email_text += '</html></body>'
            
        if user in user_emails:
            user_email = user_emails[user]
            subject = 'Today\'s Knopons'
            text = email_text
            mail(user_email, subject, text)
        if testing:
            break
