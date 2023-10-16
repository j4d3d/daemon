from tinydb import TinyDB, Query
from collections import defaultdict
import json

# load the data from your database
db = TinyDB('data/Upwork.json')
data = db.all()

# create a defaultdict
keyword_count = defaultdict(int)

# sort and print keyword frequencies
for keyword, count in sorted(keyword_count.items(), key=lambda item: item[1], reverse=False):
    print(f'{keyword}: {count}')

# iterate over the data
avg = 0
for record in data:
    value = record.get('clientSpend', 0) # get list of keywords, default to an empty list if no 'expertise' field
    print(value)
    avg += value
    keyword_count[value] += 1
avg /= len(data)
print(f'Avg: {avg:.2f}')
