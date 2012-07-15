import pymongo

from bottle import TEMPLATE_PATH, route, jinja2_template as template, request, response
from models import *
from bottle import static_file

TEMPLATE_PATH.append('./templates')

@route('/siteassets/<dir1>/:filename')
def serve_static(dir1, filename):
    return static_file(dir1 + '/' + filename, root='./siteassets/')
    
@route('/bootstrap/<dir1>/<dir2>/<dir3>/:filename')
def serve_static(dir1, dir2, dir3, filename):
    return static_file(dir1 + '/' + dir2 + '/' + dir3 + '/' + filename, root='./bootstrap/')

@route('/')
def hello_world():
    return "Hello World!!!!"

@route('/:username')
def user(username):
    users_table = pymongo.Connection('localhost', 27017)['master']['users']
    if not users_table.find_one({'username': username}):
        return 'User %s not a part of our beta test. Please wait for your invite :-)' % username
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']
    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    queries = [query for query in mainbox_table.find({'username': username})]
    deals = []
    qlen = len(queries)
    if len(queries) > 0:
        first_query = queries[0]
        deals.extend([deal for deal in deals_table.find({'query_id': first_query['_id']})])
    response.set_cookie('username', username, path = '/')    
    return template('userhome.html', username = username, queries = queries, deals = deals, qlen = qlen)
    
@route('/test/:username')
def user(username):
    users_table = pymongo.Connection('localhost', 27017)['master']['users']
    if not users_table.find_one({'username': username}):
        return 'User %s not a part of our beta test. Please wait for your invite :-)' % username
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']
    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    queries = [query for query in mainbox_table.find({'username': username})]
    deals = []
    qlen = len(queries)
    if len(queries) > 0:
        first_query = queries[0]
        deals.extend([deal for deal in deals_table.find({'query_id': first_query['_id']})])
    response.set_cookie('username', username, path = '/')    
    return template('test.html', username = username, queries = queries, deals = deals, qlen = qlen)

import string
@route('/addquery/<keyword>/<dollarlimit>')
def addquery(keyword, dollarlimit):
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']
    username = request.cookies.get('username')
    queries = [query for query in mainbox_table.find({'username': username})]
    #if(len(queries) >= 4):
    #    return {'status': 'error'}
        
    
    keyword = string.strip(keyword)
    mainbox_table.insert({'username': username, 'keyword': keyword, 'dollar_limit': dollarlimit})
    return {'status': 'ok'}

from datetime import datetime
import sys
@route('/getdealemail/<keyword>/<dollarlimit>/<days>/<username>')
def getdealemail(keyword, dollarlimit, days, username):
    dollarlimit = int(dollarlimit)
    dollarlimit = int(1.25 * dollarlimit) 
    daylimit = int(days);
    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    deals = []
    dealsout = []
    deals.extend([deal for deal in deals_table.find({'keyword': keyword, 'price': {'$lt': dollarlimit} }).sort("founddate", pymongo.DESCENDING)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        d = (datetime.utcnow() - d2).days
       
        if(d > daylimit):
            break
        deals[i]['days'] = d
        dealsout.insert(i, deals[i])
        i = i + 1
    deals = dealsout
    sys.stdout.flush()
    return template('getdealemail.html', username = username, keyword = keyword, dollarlimit = dollarlimit, deals = deals)


@route('/getdeals/<keyword>/<dollarlimit>')
def getdeals(keyword, dollarlimit):
    dollarlimit = int(dollarlimit)
    dollarlimit = int(1.25 * dollarlimit)
    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    deals = []
    print "dollarlimit:" + str(dollarlimit) + "\n"
    sys.stdout.flush()
    if(dollarlimit == -1):
        print "dollarlimit/here:" + str(dollarlimit) + "\n"
        sys.stdout.flush()
        mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']    
        queries = [query for query in mainbox_table.find({'username': keyword})]  
        qlen = len(queries)
        if(qlen == 0):
            return ""
        else:
            keyword = queries[0]['keyword']
            dollarlimit = int(queries[0]['dollar_limit'])
            print keyword + ":" + str(dollarlimit) + "\n"
            sys.stdout.flush()
    else:
        print "not -1\n"
        sys.stdout.flush()
    
    deals.extend([deal for deal in deals_table.find({'keyword': keyword, 'price': {'$lt': dollarlimit} }).sort("founddate", pymongo.DESCENDING)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        days = (datetime.utcnow() - d2).days
        deals[i]['days'] = days
        i = i + 1
    print deals
    sys.stdout.flush()
    return template('getdeals.html', keyword = keyword, dollarlimit = dollarlimit, deals = deals)
    
"""@route('/getsaveddeals/<mainboxid>/')
def getsaveddeals(mainboxid):
   
    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    deals = []
   
	saveddeals_table = pymongo.Connection('localhost', 27017)['master']['saveddeals']    
	queries = [query for query in mainbox_table.find({'mainboxid': mainboxid})]  
	qlen = len(queries)
	if(qlen == 0):
		return ""

    
    deals.extend([deal for deal in deals_table.find({ "_id": { $in: queries } }).sort("founddate", pymongo.DESCENDING)])
    i = 0
    for deal in deals:
        d2 = deal['founddate']
        days = (datetime.utcnow() - d2).days
        deals[i]['days'] = days
        i = i + 1
    print deals
    sys.stdout.flush()
    return template('getdeals.html', keyword = keyword, dollarlimit = dollarlimit, deals = deals)
"""
    
@route('/getqueries/<username>/<linkno>')
def getqueries(username, linkno):
    linkno = int(linkno)
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']    
    queries = [query for query in mainbox_table.find({'username': username})]  
    qlen = len(queries)  
    return template('getqueries.html', username = username, linkno = linkno, queries = queries, qlen = qlen)
    
    
@route('/getpopularqueries/<username>/<linkno>')
def getqueries(username, linkno):
    linkno = int(linkno)
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']    
    queries = [query for query in mainbox_table.find({'username': username})]  
    qlen = len(queries)  
    return template('getqueries.html', linkno = linkno, queries = queries, qlen = qlen)

@route('/removequery/<username>/<dollar_limit>/<keyword>')
def removequery(username, dollar_limit, keyword):
    
    mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']
    #did = bson.objectid.ObjectId(qid)
    mainbox_table.remove({'username': username, 'dollar_limit': dollar_limit, 'keyword': keyword})
    return {'status': 'ok'}
