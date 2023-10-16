import re
from tinydb import TinyDB, Query

# Setup
db = TinyDB('data/Upwork.json')

Client = Query()

field_list = ['clientPostings', 'clientSpend', 'clientHourlyRate']
for field_name in field_list:
    for item in db.all():
        if field_name in item:

            text = str(item[field_name])
            print('parsing: '+text)

            mult = 1
            if field_name == 'clientSpend':
                mat = re.search(r"(.+?)(K|M|B)?", text)
                text = mat[1]
                if mat[2] == 'K': mult = 1000
                elif mat[2] == 'M': mult = 1000000
                elif mat[2] == 'B': mult = 1000000000
            db.update({field_name: float(text) * mult}, Client[field_name] == item[field_name])