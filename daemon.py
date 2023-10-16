import sys, time, keyboard
from termcolor import colored as col
import traceback

from browser import Browser
import apis.upwork

browser = Browser()
browser.start('chrome', headless=False)

try:
    apis.upwork.log_in(browser)
    browser.wait_for_element("//div[@class='avatar-with-progress']")

    apis.upwork.search(browser, "game")
except Exception as ex:
    traceback.print_exception(type(ex), ex, ex.__traceback__)
finally:
    browser.quit()