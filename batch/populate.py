import pymongo

mainbox_table = pymongo.Connection('localhost', 27017)['master']['mainbox']

users_table = pymongo.Connection('localhost', 27017)['master']['users']

queries = [
    {'keyword': 'iphone 3g', 'dollar_limit': '200'},
    {'keyword': 'jogging stroller', 'dollar_limit': '60'},
    ]

for user in users_table.find():
    username = user['username']
    for query in queries:
        request = {}
        request.update(query)
        request.update({'username': username})
        if not mainbox_table.find_one(request):
            mainbox_table.insert(request)

