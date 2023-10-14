import sys, time, keyboard
from termcolor import colored

from browser import Browser
import apis.flex_jobs

browser = Browser()
browser.start(False)
# apis.flex_jobs.log_in(browser)
apis.flex_jobs.search(browser, "Game Programmer")

# time.sleep(5)
keyboard.wait('ctrl+left')