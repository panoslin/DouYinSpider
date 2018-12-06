#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/13/18
# IDE: PyCharm
from requests.exceptions import ConnectionError, ConnectTimeout, Timeout
from configparser import NoSectionError
from fake_useragent import UserAgent
import redis
from random import randint
import requests
import configparser
import time
from feed_api.config import request_body
from feed_api.parser import Parser

now = lambda: time.time()


class DouYin:
    def __init__(self, config="sample_config.ini", redis_connection=False):
        if config != "sample_config.ini":
            self.config = config
        else:
            PathConfig = config
            self.config = configparser.ConfigParser()
            self.config.read(PathConfig)
        self.redis_connection = redis_connection
        if redis_connection:
            self.r = self.redis()
            self.PumpOut = self.config.get("redis", "Pumpout")
        try:
            self.retry_time = config.getint('miscellaneous', 'retry_time')
            self.gap_time = config.getint('miscellaneous', 'gap_time')
        except (NoSectionError, AttributeError):
            self.retry_time = 3
            self.gap_time = 10
        self.ua = UserAgent()

    def redis(self):
        host = self.config.get("redis", "host")
        port = self.config.getint("redis", "port")
        db = self.config.getint("redis", "db")
        return redis.Redis(host=host, port=port, db=db)

    @staticmethod
    def get_random():
        """
        This method return headers and params randomly.
        :return:
        """
        RequestBody = request_body
        index = randint(0, len(RequestBody) - 1)
        return RequestBody[index]

    def get_response(self, proxy, tor, timeout, RETRY):
        """
        :param proxy: the address of the proxy
        :param tor: Boolean determine whether to use the tor proxy
        :param timeout: How many seconds to wait for the server to send data before giving up
        :param RETRY: record the remain time of retrying
        :return: requests.Response
        """
        RequestBody = self.get_random()
        headers, params, is_iphone = RequestBody['headers'], RequestBody['params'], RequestBody.get('is_iphone', False)
        try:
            if not tor:
                response = requests.post('https://api.amemv.com/aweme/v1/feed/',
                                         headers=headers,
                                         params=params,
                                         timeout=timeout)
            else:
                response = requests.post('https://api.amemv.com/aweme/v1/feed/',
                                         headers=headers,
                                         params=params,
                                         proxies=self.get_proxy(proxy),
                                         timeout=timeout)

            if response.json() is None:
                raise Timeout
            else:
                return response.json(), is_iphone
        except (ConnectTimeout, Timeout, ConnectionError):
            print('\nRetrying...')
            RETRY = self.retry_time - 1
            if RETRY <= 0:
                return None
            else:
                return self.get_response(proxy, tor, timeout, RETRY)

    @staticmethod
    def get_proxy(proxy, proxy_type='socks5'):
        """
        This is a connection to tor proxy.
        You can install Tor Browser to access this proxy.
        If the proxy server is not running, no proxy will be utilized
        :return: proxies
        """
        try:
            requests.get('http://{}'.format(proxy))
        except ConnectionError:
            return None
        proxies = {
            'http': '{}://'.format(proxy_type) + proxy,
            'https': '{}://'.format(proxy_type) + proxy
        }
        return proxies

    def post_once(self, proxy='127.0.0.1:9150', tor=True, timeout=20):
        print('\nhandshaking with the server: ', end='')
        response, is_iphone = self.get_response(proxy, tor, timeout, self.retry_time)
        res = Parser(self, response, is_iphone, self.redis_connection)
        for ele in res:
            yield ele





