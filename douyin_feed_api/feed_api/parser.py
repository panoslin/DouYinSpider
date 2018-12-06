#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/13/18
# IDE: PyCharm

import os
import time
import jmespath
import requests
import uuid

now = lambda: time.time()


def Parser(self, response, is_iphone=False, redis_connection=False):
    """
    A generator yield from the response from douyin server.
    You can overwrite this function to return your preferred content.
    :param self: DouYin instance
    :param response: The response return from the douyin server
    :param is_iphone: A boolean to identify whether the request header is ios or android
    :param redis_connection: A boolean determines whether to connect to redis
    :return: formatted data
    """
    print("\nThe response from douyin server: \n[printed by feed_api.parser.Parser]\n{res}\n\n".format(res=response))

    if redis_connection:
        for aweme in response['aweme_list']:
            if aweme['is_ads']:  # identify whether if the current video is commercial
                print('one ad found! ', end='')
                # determine whether if the video exists
                if not self.r.hexists(self.PumpOut, aweme['aweme_id']):
                    res = parse_single(aweme, self, is_iphone)
                    self.r.hset(self.PumpOut, res['aweme_id'], res)
                    yield res
                print('But it had been recorded...')
                continue
        print('Sorry, no ads were there ..')
        return
    else:
        for aweme in response['aweme_list']:
            res = parse_single(aweme, self, is_iphone)
            yield res


def parse_single(single, self, is_iphone):
    aweme = single
    res = dict()
    res['now'] = time.strftime('%Y/%m/%d', time.localtime(now()))
    res['ts'] = int(time.time())
    res['is_ads'] = aweme['is_ads']
    res['avatar_url'] = jmespath.search('author.avatar_larger.url_list[0]', aweme)
    res['register_time'] = jmespath.search('author.create_time', aweme)
    res['authorname'] = aweme['author']['nickname']
    res['author_user_id'] = jmespath.search('author_user_id', aweme)
    res['aweme_id'] = aweme['aweme_id']
    res['broadcast_time'] = aweme['create_time'] \
        if jmespath.search('create_time', aweme) \
        else jmespath.search('raw_ad_data.comment_area.comment_time', aweme)
    res['desc'] = aweme['desc'] \
        if jmespath.search('desc', aweme) \
        else jmespath.search('raw_ad_data.title', aweme)
    res['duration'] = int(str(aweme['duration'])[:-3]) \
        if jmespath.search('duration', aweme) \
        else int(jmespath.search('video.duration', aweme)) // 1000
    res['comment_count'] = jmespath.search('statistics.comment_count', aweme)
    res['digg_count'] = jmespath.search('statistics.digg_count', aweme)
    res['forward_count'] = jmespath.search('statistics.forward_count', aweme)
    res['play_count'] = jmespath.search('statistics.play_count', aweme)
    res['share_count'] = jmespath.search('statistics.share_count', aweme)
    res['video_url'] = aweme['video']['play_addr']['url_list'][0]
    height = jmespath.search('video.height', aweme)
    width = jmespath.search('video.width', aweme)
    res['vertical'] = int(int(width) < int(height))
    res['uid'] = str(uuid.uuid1())
    res['title'] = jmespath.search('raw_ad_data.comment_area.title', aweme)
    res['ad_link'] = jmespath.search('raw_ad_data.web_url', aweme)
    download_path = os.path.join('Download', 'daq', res['now'])
    file_name = res['uid'] + '.mp4'
    os.makedirs(download_path, exist_ok=True)
    res['download_path'] = os.path.join(download_path, file_name)
    RETRY = 0
    while True:
        try:
            headers = GetHeader(self, is_iphone)
            with open(res['download_path'], 'wb') as video:
                video.write(requests.get(res['video_url'], headers=headers).content)
            break
        except Exception as e:
            print('Exception {} was raised by Parser '
                  'in the statements of "with open() as video", '
                  'retrying...'.format(e))
            RETRY += 1
            if RETRY >= self.retry_time:
                return None
            else:
                continue
    res['object'] = os.path.join('daq', res['now'], file_name).replace('\\', '/')
    res['size'] = os.path.getsize(res['download_path'])
    return res


def GetHeader(self, is_iphone):
    if is_iphone:
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) "
                          "AppleWebKit/604.1.38 (KHTML, like Gecko) "
                          "Version/11.0 Mobile/15A372 Safari/604.1",
        }
        return headers
    else:
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7',
        }
        return headers
