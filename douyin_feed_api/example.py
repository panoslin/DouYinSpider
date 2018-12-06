#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/29/18
# IDE: PyCharm

from feed_api.douyin import DouYin
from feed_api.database_operation import Database
from feed_api.integratedos import FileOperation
from configparser import ConfigParser

if __name__ == '__main__':
    dy = DouYin()
    db = Database()
    file = FileOperation()

    configuration = ConfigParser()
    configuration.read('sample_config.ini')
    download_path = configuration.get('miscellaneous', 'download_path')
    oss_dst = configuration.get('miscellaneous', 'oss_dst')
    oss_console_path = configuration.get('miscellaneous', 'oss_console_path')

    res = dy.post_once()
    for ele in res:
        print(ele)

        # # upload the file to cloud
        # ans = file.read_status(path=oss_console_path)
        # if ans is True:
        #     file.merge_dir(download_path, oss_dst)
        # # run the upload program target on oss_dst

        # # database operations
        # db.operate(ele)
