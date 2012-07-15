import sys
sys.path.append('.')
import csv
from collections import defaultdict, Counter
from datetime import datetime
import pymongo

if __name__ == '__main__':
    ifile_name = sys.argv[1]

    deals_table = pymongo.Connection('localhost', 27017)['master']['deals']
    for line in csv.DictReader(open(ifile_name, 'r')):
        line['founddate'] = datetime.utcnow()
	line['price'] = float(line['price'])
        deals_table.insert(line)

