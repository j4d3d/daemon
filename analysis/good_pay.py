import json
from datetime import datetime as dt

from termcolor import colored as col

import sys
sys.path.insert(0, 'util')
import logger
from logger import log

from tinydb import TinyDB, Query
Job = Query()
db = TinyDB('data/Upwork.json')

criterion = (Job.budget > 1) | (Job.hourly > 1)
criterion = criterion & (Job.clientSpend > 0)
result = db.search(criterion)
result = sorted(result, key=lambda x: x['posted'], reverse=False)

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

    log(f"client spend: ${job['clientSpend']:,}")

    now = dt.now().timestamp()
    posted = job['posted']
    dt_posted = dt.fromtimestamp(posted)
    since = (now - posted) / (24.0 * 3600)
    # log(f"posted: {dt_posted}")
    log(f"days since: {since:.2f}")

    LINE_WIDTH = 96
    LINE_COUNT = 2

    desc = job['description'].strip()
    desc_flat = desc.replace('\n', ' ')
    
    logger.print_head_tail(desc_flat)
    # desc = desc_flat[0:48] + "...." + desc[-48:]

log(f'\nSearch yielded {len(result)} results.')