import sys, time, keyboard
from termcolor import colored as col
import traceback

from util.logger import log

from scheduler import Scheduler
from browser import Browser
import apis.upwork

class Daemon:
    def __init__(self):
        self.browser = None
        self.scheduler = None

    def start(self):
        self.browser = Browser()
        self.browser.start('chrome', headless=False)
        apis.upwork.log_in(self)

        self.scheduler = Scheduler(self)
        self.scheduler.start()
    
    def quit(self):
        if self.browser: self.browser.quit()
        if self.scheduler: self.scheduler.quit()

# try:
#     print('asdf')
# except Exception as ex:
#     traceback.print_exception(type(ex), ex, ex.__traceback__)
# finally: browser.quit()