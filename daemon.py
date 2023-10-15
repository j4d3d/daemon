import sys, time, keyboard
from termcolor import colored as col

from browser import Browser
import apis.upwork

browser = Browser()
browser.start('chrome', headless=False)

apis.upwork.log_in(browser)
# keyboard.wait('ctrl+right')
browser.wait_for_element("//div[@class='avatar-with-progress']")

apis.upwork.search(browser, "Javascript")

browser.quit()