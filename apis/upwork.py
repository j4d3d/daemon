import re
import json
import time
import keyboard
import traceback
import urllib.parse as urlparse

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from termcolor import colored as col

from tinydb import TinyDB, Query

NAME = 'Upwork'
URL_HOME = 'https://www.upwork.com/'
URL_LOGIN = 'https://www.upwork.com/ab/account-security/login'
URL_SEARCH = 'https://www.upwork.com/nx/jobs/search/?'

db = TinyDB(f"data/{NAME}.json")
Job = Query()

def log_in(browser):
    print(col("Logging In...", "magenta"))

    with open('config/auth.json') as f:
        auth = json.load(f)

    browser.get(URL_LOGIN)
    body = browser.wait_for_element("//body")
    e = browser.wait_for_element("//input[@id='login_username']")
    e.send_keys(auth[NAME]['account'])
    e = browser.wait_for_element("//button[@id='login_password_continue']")
    e.click()
    e = browser.wait_for_element("//input[@id='login_password']")
    e.send_keys(auth[NAME]['password'])
    e = browser.wait_for_element("//button[@id='login_control_continue']")
    e.send_keys(Keys.RETURN)
    browser.wait_for_stale(e)
    print(col(f'Logged into {NAME} successfully', 'cyan'))

def search(browser, query):
    print(col(f"Searching {NAME} for \"{query}\"...", "magenta"))

    params = {
        'q': query,
        'user_location_match': 2,
        'sort': 'recency'
    }
    url = URL_SEARCH + urlparse.urlencode(params)
    browser.get(url)

    # wait for sections to load
    e = browser.wait_for_element("//div[contains(@data-test, 'job-tile-list')]/section")

    e = browser.wait_for_element("//div[contains(@data-test, 'job-tile-list')]")
    job_cells = e.find_elements(By.XPATH, ".//section")

    new_jobs = []

    for cell in job_cells:
        data = {}

        # get id
        e = browser.wait_for_child_of(cell, ".//a[contains(@class, 'up-n-link')]")
        href = e.get_attribute('href')
        print(href)
        data['id'] = re.match(r".+~(.+)/", href)[1]
        print('id: '+data['id'])

        # do we already have this job?
        result = db.search(Job['id'] == data['id'])
        if result: continue

        cell.click()
        content = browser.wait_for_element("//div[contains(@data-test, 'job-details-viewer')]")
        # time.sleep(1)

        data['id'] = re.match('.+~(.+?)\?', browser.driver.current_url)[1]
        print(col(f"Job Id: {data['id']}", 'cyan'))

        # parse this job and add to DB
        try:
            if False:
                e = browser.find_child_of(content, ".//header[contains(@class, 'up-card-header d-flex')]")
                if e is not None:
                    data['title'] = e.text

                e = browser.find_child_of(content, ".//span[contains(@data-test, 'up-c-relative-time')]")
                if e is not None:
                    data['posted'] = e.text

                # e = browser.wait_for_child_of(content, ".//div[contains(@class, 'cfe-ui-job-breadcrumbs')]")
                # data['breadcrumbs'] = e.text

                e = browser.find_child_of(content, ".//div[contains(@data-test, 'job-currency-render')]")
                if e is not None:
                    data['budget'] = e.text

                e = browser.find_child_of(content, ".//div[contains(@data-test, 'description')]")
                if e is not None:
                    data['description'] = e.text

                e = browser.find_child_of(content, "//aside/*[contains(@data-test, 'connects-auction')]")
                if e is not None:
                    print(e.text)
                    data['connects'] = re.match("Send a proposal for:\s+(\d+) Connects", e.text)[1]
                else: print(col(content.get_attribute('innerHTML'), 'red'))

                e = browser.find_child_of(content, "//aside/*[contains(@data-test, 'client-spend')]")
                if e is not None:
                    mat = re.match("$(.+?) total spent", e.text)
                    data['clientSpent'] = mat[1]

                e = browser.find_child_of(content, "//aside/*[contains(@data-test, 'client-job-posting-stats')]")
                if e is not None:
                    mat = re.match("(.+?) jobs posted", e.text)
                    data['clientPostCount'] = mat[1]
                
                e = browser.find_child_of(content, "//aside/*[contains(@data-test, 'client-hires')]")
                if e is not None:
                    mat = re.match("(\d+) hires(?:, (\d+) active)", e.text)
                    data['clientHires'] = mat[1]
                    data['clientActive'] = mat[2]
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            # print(col(content.get_attribute('innerHTML'), 'red'))


        # now use soup to parse side panel
        soup = BeautifulSoup(content.get_attribute("innerHTML"), 'html.parser')
        
        souples = [['description', 'data-test', 'description', r"(.*)"],
                   ['connects', 'data-test', 'connects-auction', r"(\d+) Connects"],
                   ['clientPostings', 'data-qa', 'client-job-posting-stats', r"(\d+)\s*jobs?\s*posted"],
                   ['clientSpend', 'data-qa', 'client-spend', r"\$([^\s]+)"],
                   ['clientHourlyRate', 'data-qa', 'client-hourly-rate', r"\$([^\s]+)"],
                   ['clientHours', 'data-qa', 'client-hours', r"([^\s]+)\s*hours?"],
                   ['clientHires', 'data-test', 'client-hires', r"(.*)"],
                   ['currency', 'data-test', 'job-currency-render', r"\$([^\s]+)"]
        ]
                   
        for souple in souples:
            se = soup.find(attrs={souple[1]: souple[2]})
            if se is not None: 
                text = se.text.replace('\n', ' ')
                print(f"{souple} -> {text}")
                data[souple[0]] = re.search(souple[3], text, re.DOTALL)[1]


        print(col(json.dumps(data, indent=2), "green"))

        keyboard.wait('ctrl+down')
        db.insert(data)
        browser.driver.back()
        
    return new_jobs