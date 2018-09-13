#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2018/8/22
# IDE: PyCharm

from random import choice
import time
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from random import randint


def swipe():
    """
    swipe on the emulator
    :return:
    """
    time.sleep(1)
    TouchAction(driver).press(x=randint(200, 500), y=940).move_to(x=randint(200, 500), y=200).release().perform()

def StartDriver():
    """
    connect to the appium server
    :return: driver
    """
    global StartTime
    StartTime = int(time.time())
    # The necessary parms to convert to appium server
    caps = {}
    caps["platformName"] = "Android"
    caps["deviceName"] = "SAMSUNG_SM_N900A"
    # Next two ele can be found by bash command:
    # adb logcat ActivityManager:I*:s
    caps["appPackage"] = "com.ss.android.ugc.aweme"  # DouYin package adress
    caps["appActivity"] = ".main.MainActivity"  # DouYin lauching activity
    # Remote driver connection to appium server
    global driver
    driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
    swipe()

def main():
    """
    The main swipe action, restart every 30mins
    :return:
    """
    StartDriver()
    # Start to loop the action chain
    while (int(time.time()) - StartTime) % 1800 != 0:  # Restart every 30mins
        next = choice(
            ['fit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit',
             'Notfit', 'Notfit'])  # one fit in 2 request(i.e. 12 videos)
        if next == 'fit':
            time.sleep(randint(30, 80))
            swipe()
        elif next == 'Notfit':
            swipe()
    driver.close_app()

if __name__ == '__main__':
    # This sample code uses the Appium python client
    # pip install Appium-Python-Client
    # Start to loop the action chain
    # and capture any errors occur
    while True:
        try:
            main()
        except Exception as e:
            print('Exception raised {Exception}'.format(Exception=e))
            StartDriver()
            continue
