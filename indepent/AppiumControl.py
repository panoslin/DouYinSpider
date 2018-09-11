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
    time.sleep(2)
    TouchAction(driver).press(x=randint(200, 500), y=940).move_to(x=randint(200, 500), y=200).release().perform()


if __name__ == '__main__':
    # This sample code uses the Appium python client
    # pip install Appium-Python-Client
    # Then you can paste this into a file and simply run with Python

    caps = {}
    caps["platformName"] = "Android"
    caps["deviceName"] = "SAMSUNG_SM_N900A"
    caps["appPackage"] = "com.ss.android.ugc.aweme"
    caps["appActivity"] = ".main.MainActivity"

    driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
    swipe()
    while True:
        next = choice(
            ['fit', 'Notfit', 'Notfit', 'Notfit', 'Notfit', 'Notfit'])  # one fit in one request(i.e. six videos)
        if next == 'fit':
            time.sleep(randint(5, 40))
            TouchAction(driver).tap(x=658, y=452).perform()
            swipe()
            swipe()
            # time.sleep(2)
            # TouchAction(driver).tap(x=357, y=935).perform()
            # time.sleep(randint(5, 40))
            # TouchAction(driver).tap(x=50, y=109).perform()
            time.sleep(2)
            TouchAction(driver).tap(x=50, y=109).perform()
            swipe()

        elif next == 'Notfit':
            swipe()
