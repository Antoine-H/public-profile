import httplib2,json
import zlib
import zipfile
import sys
import re
import time
import datetime
import operator
import sqlite3
import os
import locale
from datetime import datetime
from datetime import date
import pytz
from tzlocal import get_localzone
import requests
from termcolor import colored, cprint
from pygraphml import *
from pygraphml.graph import *
from pygraphml.node import *
from pygraphml.edge import *

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from io import StringIO

linkedin_username = ""
linkedin_password = ""

chromeOptions = webdriver.ChromeOptions()
prefs  = {"profile.managed_default_content_settings.images":2,
          "profile.default_content_setting_values.notifications":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)


def loginLinkedin(driver):
    driver.implicitly_wait(120)
    driver.get("https://www.linkedin.com/")
    assert "LinkedIn: Log In or Sign Up" in driver.title
    time.sleep(3)
    driver.find_element_by_id("login-email").send_keys(linkedin_username)
    driver.find_element_by_id("login-password").send_keys(linkedin_password)
    driver.find_element_by_id("login-submit").click()
    global all_cookies
    all_cookies = driver.get_cookies()
    html = driver.page_source
    if "Incorrect Email/Password Combination" in html:
        print("[!] Incorrect Facebook username (email address) or password")
        sys.exit()


