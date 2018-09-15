#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2018/8/22
# IDE: PyCharm

import time
from appium import webdriver


class Action():
    def __init__(self):
        """
        connect to the appium server
        :return: driver
        """
        self.StartTime = int(time.time())
        # The necessary parms to convert to appium server
        caps = {}
        caps["platformName"] = "Android"
        caps["deviceName"] = "SAMSUNG_SM_N900A"
        # Next two ele can be found by bash command:
        # adb logcat ActivityManager:I*:s
        caps["appPackage"] = "com.ss.android.ugc.aweme"  # DouYin package adress
        caps["appActivity"] = ".main.MainActivity"  # DouYin lauching activity
        caps["newCommandTimeout"] = 0
        # Remote driver connection to appium server
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
        print('Connected to the appium server')

    def main(self):
        """
        Rsstart over and over again
        cause every time it restart, it will get one request and
        return one response which is in json format with infos about 6 upcoming videos
        :return: None
        """
        while True:
            time.sleep(5)
            self.driver.reset()


if __name__ == '__main__':
    # This sample code uses the Appium python client
    # pip install Appium-Python-Client
    # capture any errors occur
    action = Action()
    while True:
        try:
            action.main()
        except Exception as e:
            print('Exception raised {Exception}'.format(Exception=e))
            action = Action()
            continue
