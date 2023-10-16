from tinydb import TinyDB, Query
from collections import defaultdict
import json

# load the data from your database
db = TinyDB('data/old_Upwork.json')
data = db.all()

# create a defaultdict
keyword_count = defaultdict(int)

# iterate over the data
for record in data:
    expertise_list = record.get('expertise',[]) # get list of keywords, default to an empty list if no 'expertise' field
    for keyword in expertise_list:
        keyword_count[keyword] += 1 # increment count of keyword

# sort and print keyword frequencies
for keyword, count in sorted(keyword_count.items(), key=lambda item: item[1], reverse=False):
    print(f'{keyword}: {count}')