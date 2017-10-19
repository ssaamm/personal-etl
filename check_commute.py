"""
usage:

    get_commute.py '123 sesame street, city, tx' '555 abc ave, city2, tx' 16 '+15551234567'
"""
from __future__ import print_function

import time
import sys
import os

from twilio.rest import Client
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'http://maps.google.com'
HOME, WORK, WARN_WHEN, WARN_NUMBER = sys.argv[1:5]
WARN_MINS = int(WARN_WHEN)

twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
token = os.getenv('TWILIO_TOKEN')
my_number = os.getenv('MY_NUMBER')

def get_transit_time(from_addr, to_addr, driver):
    try:
        element = driver.find_element_by_id('ml-searchboxinput')
        element.send_keys(HOME, Keys.ENTER)
        time.sleep(1)

        element = driver.find_element_by_class_name('ml-white-circle')
        element.click()
        time.sleep(1)

        element = driver.find_element_by_id('ml-waypoint-input-0')
        element.send_keys(WORK, Keys.ENTER)
        time.sleep(1)

        element = driver.find_element_by_class_name('ml-directions-pane-header-time-content')
        return element.text
    except Exception as x:
        print('problem', x)
    finally:
        driver.quit()


client = Client(twilio_account_sid, token)

def message(recipient, body):
    client.messages.create(to=recipient, from_=my_number, body=body)

if __name__ == '__main__':
    driver = webdriver.PhantomJS()
    driver.set_window_size(1039, 781)
    driver.get(URL)
    driver.implicitly_wait(10)

    transit_time = get_transit_time(HOME, WORK, driver)
    print(transit_time)
    split = transit_time.split()
    transit_time_mins = int(split[0])

    if transit_time_mins >= WARN_MINS or len(split) != 2 or split[1] != 'min':
        print('Warning', WARN_NUMBER)
        message(WARN_NUMBER, 'Hey, commute is long ({})'.format(transit_time))
