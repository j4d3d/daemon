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

db = TinyDB(f"data/{NAME}.json", indent=4)
Job = Query()

def log_in(daemon):
    browser = daemon.browser
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

def search(daemon, query, max_page=999999):
    browser = daemon.browser
    log(col(f"Searching {NAME} for \"{query}\"...", "magenta"))

    quit = False

    page = 1
    while not quit:

        if page > 1:
            log('zzz')
            time.sleep(7)

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
        if e is None: 
            log("job-tile-list never loaded.")
            break

        job_cells = e.find_elements(By.XPATH, ".//section")

        new_jobs = []

        for cell in job_cells:
            data = {}

            # get id
            e = browser.wait_for_child_of(cell, ".//a")
            if e is None: continue

            data['title'] = e.text.strip()
            href = e.get_attribute('href')
            data['id'] = re.match(r".+~(.+)/", href)[1]
            log(col(f"Job Id: {data['id']}", 'cyan'))

            # do we already have this job?
            result = db.search(Job['id'] == data['id'])
            if result: continue

            # click the 'More' button
            if False:
                e = browser.wait_for_child_of(cell, ".//button[contains(text, 'More')]")
                if e:
                    log(f"Found button: {e.text}")
                    e.click()
                else: log("No button found")
                browser.wait_for_element(".//div[contains(data-test, 'job-description-text')]")

            parse_cell(cell, data)

            # cell.click()
            # content = browser.wait_for_element("//div[contains(@data-test, 'job-details-viewer')]")
            # parse_content(content, data)

            # time.sleep(1)

            # now use soup to parse side panel

            if helper.wait_for_arrow():
                db.insert(data)
            else:
                quit = True
                break
        if quit: break

        page += 1
        if (max_page != -1 and page > max_page):
            break
        time.sleep(1)

        # next page if available
        btn_next = browser.find_element("//button[normalize-space(.)='Next']")
        if btn_next is None or btn_next.get_attribute('disabled') is not None: 
            break
        log(col(f"Search for '{query}' advancing to page {page}...", "magenta"))
        btn_next.click()
        
    return new_jobs

def expand_data(daemon, data):
    browser = daemon.browser
    url = "https://www.upwork.com/jobs/~" + data['id']
    browser.get(url)
    # todo: finish

def parse_cell(cell, data):
    data['source'] = 'condensed'
    soup = BeautifulSoup(cell.get_attribute("innerHTML"), 'html.parser')

    souples = [
            ['jobType', 'data-test', 'job-type', "(.*)"],
            ['hourly', 'data-test', 'job-type', "(.*)"],
            ['budget', 'data-test', 'budget', ".*\$([^\s]+)"],
            ['duration', 'data-test', 'duration', "(.*)"],
            ['posted', 'data-test', 'UpCRelativeTime', "(.*)"],
            ['description', 'data-test', 'job-description-text', "(.*)"],
            ['clientVerification', 'data-test', 'payment-verification-status', "(.*)"],
            ['clientSpend', 'data-test', 'client-spendings', "(.*)"],
            ['clientCountry', 'data-test', 'client-country', "(.*)"],
            ['skills', 'class', 'up-skill-wrapper', None],
    ]

    float_fields = ['budget']#'clientPostings', 'clientHourlyRate', 'clientHours', 'clientHires', 'currency' ]

    for souple in souples:
        se = soup.find(attrs={souple[1]: souple[2]})
        if se is not None: 
            if souple[3] is not None:
                field = se.text.replace(',', '').strip()
                log(field)
                field = re.search(souple[3], field, re.DOTALL)[1]
                if len(field) == 0: continue
                if souple[0] in float_fields: field = float(field)
                data[souple[0]] = field
            else: data[souple[0]] = str(se)
    
    parse_data(data)
    # skills = []
    # e = soup.find(attrs={'class': 'up-skill-wrapper'})
    # for a in e.find_all('a'):
    #     skills.append(a.text.strip())
    # data['skills'] = skills

    # data['raw'] = cell.get_attribute("innerHTML")

def parse_content(content, data):
    data['source'] = 'expanded'
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
    parse_data(data)
    
def parse_data(data):
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
        data['expertise'] = [e.text.strip() for e in BeautifulSoup(data['expertise'], 'html.parser').find_all('li')]
        # data['skills'] = data['expertise']
        # del data['expertise']
    if 'skills' in data:
        data['skills'] = [e.text.strip() for e in BeautifulSoup(data['skills'], 'html.parser').find_all('a')]
    if 'clientSpend' in data:
        text = data['clientSpend']
        log(f"parsing spend: {text}")
        mat = re.search(r"^\$?([^\s]+?)(K|M|B|)", text.strip())
        text = mat[1]
        mult = 1
        if mat[2] == 'K': mult = 1000
        elif mat[2] == 'M': mult = 1000000
        elif mat[2] == 'B': mult = 1000000000
        data['clientSpend'] = float(text) * mult
        log(data['clientSpend'])
    if 'hourly' in data:
        text = data['hourly'].replace(',', '').strip()
        log('re: '+text)
        mat = re.search(r"\$([^\-]+)(?:\-\$(.+))?", text)
        log(f"mat: {mat}")
        if mat is not None and mat[1] is not None:
            hourly = float(mat[1])
            if mat[2] is not None:
                hourly = (hourly + float(mat[2])) / 2
            data['hourly'] = hourly
        else: del data['hourly']
    
    log(col(json.dumps(data, indent=2), "green"))