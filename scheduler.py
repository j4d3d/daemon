import time
import keyboard
import threading
from datetime import datetime as dt
from termcolor import colored as col

from util.logger import log

import apis.upwork

class Scheduler():

    def __init__(self, daemon):
        self.daemon = daemon
        self.stop = False
        self.queue_search = ['game programming']#, 'unity', 'web scraping', 'etl', 'automation']

    def start(self):
        now = dt.now()
        log(col(f"Starting Scheduler at {now}, t {now.timestamp}", 'cyan'))
        self.start_time = now.timestamp
        goal_time = dt(now.year, now.month, now.day, now.hour + 1)
        log(col(f"Next call: {goal_time}", "cyan"))

        def update():
            log('Updating...')
            self.run_searches()

        update()
        if False:
            delay = goal_time.timestamp() - dt.now().timestamp()
            log(f'delay: {delay}')
            time.sleep(delay)
            while (True):
                update()
                time.sleep(3600)

        # self.thread = threading.Thread(target=update)
        # self.thread.start()

    def quit(self):
        self.stop = True
        # self.thread.join()

    def run_searches(self):
        for search in self.queue_search:
            apis.upwork.search(self.daemon, search, max_page=7)
            # break