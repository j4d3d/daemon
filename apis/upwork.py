import re
import json
import time, datetime
import keyboard
import traceback
import urllib.parse as urlparse
import helper

from util.logger import log

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
    log(col("Logging In...", "magenta"))

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
    browser.wait_for_element("//div[@class='avatar-with-progress']")
    log(col(f'Logged into {NAME} successfully', 'cyan'))

def search(browser, query, max_page=999999):
    log(col(f"Searching {NAME} for \"{query}\"...", "magenta"))

    quit = False

    page = 1
    while (not quit) and (max_page == -1 or page <= max_page):

        params = {
            'q': query,
            'user_location_match': 2,
            'sort': 'recency',
        }
        if page > 1: params['page'] = page
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
            data['title'] = e.text.strip()
            href = e.get_attribute('href')
            data['id'] = re.match(r".+~(.+)/", href)[1]
            log(col(f"Job Id: {data['id']}", 'cyan'))

            # do we already have this job?
            result = db.search(Job['id'] == data['id'])
            if result: continue

            cell.click()
            content = browser.wait_for_element("//div[contains(@data-test, 'job-details-viewer')]")
            # time.sleep(1)

            # now use soup to parse side panel
            soup = BeautifulSoup(content.get_attribute("innerHTML"), 'html.parser')
            
            souples = [
                    ['posted', 'data-test', 'up-c-relative-time', r"(.*)"],
                    ['description', 'data-test', 'description', r"(.*)"],
                    ['connects', 'data-test', 'connects-auction', r"(\d+) Connects"],
                    ['clientPostings', 'data-qa', 'client-job-posting-stats', r"(\d+)\s*jobs?\s*posted"],
                    ['clientSpend', 'data-qa', 'client-spend', r"\$([^\s]+)"],
                    ['clientHourlyRate', 'data-qa', 'client-hourly-rate', r"\$([^\s]+)"],
                    ['clientHours', 'data-qa', 'client-hours', r"([^\s]+)\s*hours?"],
                    ['clientHires', 'data-test', 'client-hires', r"(.*)"],
                    ['currency', 'data-test', 'job-currency-render', r"\$([^\s]+)"],
                    ['expertise', 'data-test', 'expertise', None],
            ]

            float_fields = ['clientPostings', 'clientHourlyRate', 'clientHours', 'clientHires', 'currency' ]

            for souple in souples:
                se = soup.find(attrs={souple[1]: souple[2]})
                if se is not None: 
                    if souple[3] is not None:
                        field = re.search(souple[3], se.text, re.DOTALL)[1]
                        if souple[0] in float_fields: field = float(field.replace(',', ''))
                        data[souple[0]] = field
                    else: data[souple[0]] = str(se)
                    # log(f"{souple} -> {data[souple[0]]}")
            
            # special parsing for some fields
            if 'posted' in data:
                time = datetime.datetime.now().timestamp()
                # log(f"Parsing {data['posted']} at time: {time} {datetime.datetime.utcnow()}")
                mat = re.search(r"(?:Posted\s+)?(\w+)\s+(second|minute|hour|day|week|month|year)s?\s+ago", data['posted'])
                quant = float(mat[1])
                if mat[2] == 'second': time -= quant
                elif mat[2] == 'minute': time -= 60 * quant
                elif mat[2] == 'hour': time -= 3600 * quant
                elif mat[2] == 'day': time -= 3600 * 24 * quant
                elif mat[2] == 'week': time -= 3600 * 24 * 7 
                elif mat[2] == 'year': time -= 3600 * 24 * 365.25 * quant
                data['posted'] = int(time)
            if 'expertise' in data:
                data['expertise'] = [li.text.strip() for li in BeautifulSoup(data['expertise'], 'html.parser').find_all('li')]
            if 'clientSpend' in data:
                text = data['clientSpend']
                log(f"parsing spend: {text}")
                mat = re.search(r"^([^\s]+?)(K|M|B)?$", text.strip())
                text = mat[1]
                mult = 1
                if mat[2] == 'K': mult = 1000
                elif mat[2] == 'M': mult = 1000000
                elif mat[2] == 'B': mult = 1000000000
                data['clientSpend'] = float(text) * mult
                log(data['clientSpend'])
            
            log(col(json.dumps(data, indent=2), "green"))

            if helper.wait_for_arrow():
                db.insert(data)
                browser.driver.back()
            else:
                quit = True
                break
        if quit: break

        # next page if available
        btn_next = browser.find_element("//button[normalize-space(.)='Next']")
        if btn_next is None or btn_next.get_attribute('disabled') is not None: 
            break
        page += 1
        log(col(f"Search for '{query}' advancing to page {page}...", "magenta"))
        # btn_next.click()
        
    return new_jobs