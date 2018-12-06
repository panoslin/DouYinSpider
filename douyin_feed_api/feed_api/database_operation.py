#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/29/18
# IDE: PyCharm

from feed_api.mysql_switch import MysqlSwitch
from configparser import NoSectionError
import configparser
import time
import json

class Database:
    def __init__(self, config="sample_config.ini"):
        """
        This class receives a config file containing field necessary
        to insert/update/delete/etc into the corresponding tables in some databases.

        The following methods like insert_videobase_and_userfile() are some example.
        You can modified it as your need.

        The last method operate() make a bundle operation
        and commit the operation to the database
        operate() is decorated by MysqlSwitch.
        MysqlSwitch provides the necessaty keyword arguments(i.e. **kwargs) to the decorated function.
        Such as connection and cursor to the database.
        And commit the operation if without Exception during the operation
        or else the operation will be rollback and raise the corresponding Exception
        See more about MysqlSwitch in its doc

        :param config: a config file configparser.ConfigParser() or a path to the config file
        """
        if config != "sample_config.ini":
            self.config = config
        else:
            PathConfig = config
            self.config = configparser.ConfigParser()
            self.config.read(PathConfig)
        try:
            self.src = self.config.getint('miscellaneous', 'src')
            self.from_ = self.config.getint('miscellaneous', 'media_id')
        except (NoSectionError, AttributeError):
            self.src = 0000
            self.from_ = '0000'

        self.tables = ['video_table', 'user_table', 'local_video_backup', 'video_statistics']

    def insert_videobase_and_userfile(self, data, **kwargs):
        privacy = 13
        market_location = '中国'
        from_ = self.from_
        user_id = 53186
        mime_type = 'video'
        status = 13
        D = {
            'title': data['authorname'],
            'introduction': data['desc'],
            'privacy': privacy,
            'created_at': data['ts'],
            'updated_at': data['ts'],
            'market_location': market_location,
            'market_year': int(data['broadcast_time']),
            'from': from_,
            'user_id': user_id,
            'vertical': data['vertical'],
            'orginal_info': data['digg_count']
        }
        ES = (
            "INSERT INTO {table} ( `title`, `introduction`, `privacy`, "
            "`created_at`, `updated_at`, `market_location`, `market_year`, "
            "`from`, `user_id`, `vertical`, `orginal_info`  ) "
            "VALUES "
            "( %(title)s, %(introduction)s, %(privacy)s, "
            "%(created_at)s, %(updated_at)s, %(market_location)s, %(market_year)s, "
            "%(from)s, %(user_id)s, %(vertical)s, %(orginal_info)s );".format(table=self.tables[0]))

        kwargs['cur'].execute(ES, D)
        lastrowid = kwargs['cur'].lastrowid

        D = {
            'user_id': user_id,
            'object': data['object'],
            'name': data['authorname'],
            'size': data['size'],
            'description': data['desc'],
            'mime_type': mime_type,
            'mime_id': lastrowid,
            'status': status,
            'created_at': data['ts'],
            'updated_at': data['ts'],
        }
        ES = (
            "INSERT INTO {table} ( `user_id`, `object`, `name`, `size`, `description`, "
            "`mime_type`, `mime_id`, `status`, `created_at`, `updated_at` ) "
            "VALUES "
            "( %(user_id)s, %(object)s, %(name)s, %(size)s, %(description)s, "
            "%(mime_type)s, %(mime_id)s, %(status)s, %(created_at)s, %(updated_at)s );".format(table=self.tables[1]))
        kwargs['cur'].execute(ES, D)
        return lastrowid

    def insert_crawvideo(self, data, lastrowid, **kwargs):
        infofrom = 'Douyin'
        crawname = self.from_
        language = 'Chinese'
        region = 'China'
        D = {
            'createtime': data['ts'],
            'updatetime': data['ts'],
            'broadcasttime': time.strftime('%Y%m%d', time.localtime(data['broadcast_time'])),
            'tvcbookid': lastrowid,
            'infofrom': infofrom,
            'crawname': crawname,
            'broadcastid': data['aweme_id'],
            'broadcastname': data['authorname'],
            'broadcastdesc': data['desc'],
            'broadcastauthorid': data['author_user_id'],
            'broadcastauthorname': data['authorname'],
            'language': language,
            'region': region,
            'likes': data['digg_count'],
            'comments': data['comment_count'],
            'alljson': json.dumps(data),
            'duration': data['duration'],
            'vertical': data['vertical'],
        }

        ES = (
            "INSERT INTO {table} ( `createtime`, `updatetime`, `broadcasttime`, `tvcbookid`, `infofrom`, "
            "`crawname`, `broadcastid`, `broadcastname`, `broadcastdesc`, `broadcastauthorid`, "
            "`broadcastauthorname`, `language`, `region`, `likes`, `comments`, `alljson`, "
            "`duration`, `vertical` ) "
            "VALUES "
            "( %(createtime)s, %(updatetime)s, %(broadcasttime)s, %(tvcbookid)s, %(infofrom)s, "
            "%(crawname)s, %(broadcastid)s, %(broadcastname)s, %(broadcastdesc)s, %(broadcastauthorid)s, "
            "%(broadcastauthorname)s, %(language)s, %(region)s, %(likes)s, %(comments)s, %(alljson)s, "
            "%(duration)s, %(vertical)s );".format(table=self.tables[2]))
        kwargs['cur_local'].execute(ES, D)

    def insert_yii2_video_src_info(self, data, lastrowid, **kwargs):

        D = {
            'video_id': lastrowid,
            'media_id': self.from_,
            'media_url': data['video_url'],
            'views': data['play_count'],
            'likes': data['digg_count'],
            'comments': data['comment_count'],
            'favorited': None,
            'shared': data['share_count'],
            'created_at': data['ts'],
            'updated_at': data['ts'],
            'src': self.src,
            'market_year': data['broadcast_time']}
        ES = (
            "INSERT INTO {table} ( `video_id`, `media_id`, `media_url`, `views`, `likes`, "
            "`comments`, `favorited`, `shared`, `created_at`, `updated_at`, `src`, `market_year`) "
            "VALUES "
            "( %(video_id)s, %(media_id)s, %(media_url)s, %(views)s, %(likes)s, %(comments)s, "
            "%(favorited)s, %(shared)s, %(created_at)s, %(updated_at)s, %(src)s, %(market_year)s);".format(
                table=self.tables[3]))
        kwargs['cur'].execute(ES, D)

    @MysqlSwitch()
    def operate(self, data, **kwargs):
        # rewrite the following methods
        lastrowid = self.insert_videobase_and_userfile(data, **kwargs)
        self.insert_crawvideo(data, lastrowid, **kwargs)
        self.insert_yii2_video_src_info(data, lastrowid, **kwargs)
