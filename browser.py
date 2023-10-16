import time
import logging

from urllib import parse
from termcolor import colored as col

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchWindowException, TimeoutException
from selenium.webdriver.support.expected_conditions import staleness_of

class Browser():
    def __init__(self):
        pass

    def old_start(self, headless=True):
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
        options.page_load_strategy = 'normal' # none, eager, normal
        print('Opening webdriver')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        self.driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
        self.driver.set_page_load_timeout(30)
        self.driver.set_script_timeout(30)

        logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        logger.setLevel(logging.WARNING)

        self.driver.set_window_size(1620, 1080) 

    def start(self, type='chrome', headless=True):
        def set_options(options):
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

        if type == 'chrome':
            options = ChromeOptions()
            set_options(options)
            self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        elif type == 'firefox':
            options = FirefoxOptions()
            set_options(options)
            self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        elif type == 'edge':
            options = EdgeOptions()
            set_options(options)
            self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
        else:
            print("Driver type is not supported.")
            self.driver = None

        self.driver.set_page_load_timeout(10)
        self.driver.set_script_timeout(10)

        logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
        logger.setLevel(logging.WARNING)

        self.driver.set_window_size(1620, 1080)
    
    def quit(self):
        print(col("Exiting browser... ", "red") + col(' '+str(self.driver), "grey"))
        self.driver.quit()

    def get(self, url):
        self.driver.get(url)
        time.sleep(1)
    
    def wait_for_element(self, query, by=By.XPATH, wait=10):
        element = None
        try: element = WebDriverWait(self.driver, wait).until(
            EC.element_to_be_clickable((by, query)))
        finally: 
            found = str(element)
            if (len(found) > 12): found = found[:9] + '...'
            print(f'Wait done, found: {found}, criteria: ({by}) {query}')
            return element
        
    def wait_for_child_of(self, parent, query, by=By.XPATH, wait=10):
        element = None
        try: element = WebDriverWait(parent, wait).until(
            EC.element_to_be_clickable((by, query)))
        finally: 
            found = str(element)
            if (len(found) > 12): found = found[:9] + '...'
            print(f'Wait done, found: {found}, criteria: ({by}) {query}')
            return element
    
    def wait_for_stale(self, element, timeout=30):
        yield
        WebDriverWait(self.driver, timeout).until( staleness_of(element) )
        time.sleep(.333)

    def find_element(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)

    def find_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)
    
    def find_child_of(self, parent, xpath):
        try:
            e = parent.find_element(By.XPATH, xpath)
            return e
        except:
            return None