import json
import urllib.parse as urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from termcolor import colored as col

NAME = 'FlexJobs'
URL_HOME = 'https://www.flexjobs.com/'
URL_LOGIN = 'https://www.flexjobs.com/login'
URL_SEARCH = 'https://www.flexjobs.com/search?'

def log_in(browser):
    with open('config/auth.json') as f:
        auth = json.load(f)

    browser.get(URL_LOGIN)
    body = browser.wait_for_element("//body")
    e = browser.wait_for_element("//input[@id='name']")
    e.send_keys(auth[NAME]['account'])
    e = browser.wait_for_element("//input[@id='password']")
    e.send_keys(auth[NAME]['password'])
    e.send_keys(Keys.RETURN)
    browser.wait_for_stale(e)
    print(col(f'Logged into {NAME} successfully', 'cyan'))

def search(browser, query):
    params = {
        'search': query,
        'location': 'Remote'
    }
    url = URL_SEARCH + urlparse.urlencode(params)
    print(url)
    browser.get(url)

    e = browser.wait_for_element("//ul[@id='job-list']")
    job_cells = e.find_elements(By.XPATH, ".//li")

    for cell in job_cells:
        print('\nCell: \n' + cell.text)
    print(f"{len(job_cells)} {job_cells}")

    return job_cells