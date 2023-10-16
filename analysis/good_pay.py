import json
from datetime import datetime as dt

from termcolor import colored as col

import sys
sys.path.insert(0, 'util')
from logger import log

from tinydb import TinyDB, Query
Job = Query()
db = TinyDB('data/Upwork.json')

result = db.search((Job.budget > 1) | (Job.hourly > 1))
result = sorted(result, key=lambda x: x['posted'])

for job in result:
    # print(json.dumps(job, indent=4))
    log(f"{col(job['title'], 'white')}")

    url = f"https://www.upwork.com/jobs/~{job['id']}"
    log(col(url, 'cyan'))

    pay_key = 'hourly'
    color = 'cyan'
    if 'budget' in job: 
        pay_key = 'budget'
        color = 'green'
    pay_print = f"{pay_key}: ${col(job[pay_key], color)}"
    log(pay_print)

    now = dt.now().timestamp()
    posted = job['posted']
    since = (now - posted) / (24.0 * 3600)
    log(f"days since: {since:.2f}")

    desc = job['description']
    desc = desc[0:48] + "...." + desc[-48:]
    log(f"description: {desc}")