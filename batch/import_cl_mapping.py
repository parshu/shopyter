import sys
sys.path.append('.')
import csv
from collections import defaultdict, Counter
from datetime import datetime
import pymongo

if __name__ == '__main__':
    ifile_name = sys.argv[1]
    dbname = sys.argv[2]

    mapping_table = pymongo.Connection('localhost', 27017)[dbname]['clmapping']
    for line in csv.DictReader(open(ifile_name, 'r')):
        mapping_table.insert(line)

