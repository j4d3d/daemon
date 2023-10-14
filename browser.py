import time
import logging

from urllib import parse
from termcolor import colored

from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, TimeoutException
from selenium.webdriver.support.expected_conditions import staleness_of

class Browser():
    def __init__(self):
        pass

    def start(self, headless=True):
        options = webdriver.ChromeOptions()
        # options.add_argument("--window-size=1620x1080")
        # options.add_argument('--headless')
        if headless: options.add_argument('--headless=new')
        # options.add_argument('--no-sandbox')
        # options.add_experimental_option("detach", True) # doesn't work
        # options.add_argument("start-maximized")
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        options.page_load_strategy = 'none' # none, eager, normal
        print('Opening webdriver')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.set_page_load_timeout(10)
        self.driver.set_script_timeout(10)

        logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        logger.setLevel(logging.WARNING)

    def get(self, url):
        self.driver.get(url)
    
    def wait_for_element(self, query, by=By.XPATH):
        element = None
        try: element = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((by, query)))
        finally: 
            found = str(element)
            if (len(found) > 12): found = found[:9] + '...'
            print(f'wait done, found: {found}, criteria: ({by}) {query}')
            return element
    
    def wait_for_stale(self, element, timeout=30):
        yield
        WebDriverWait(self.driver, timeout).until( staleness_of(element) )
        time.sleep(.333)

    def find_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)