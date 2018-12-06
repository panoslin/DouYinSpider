#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/29/18
# IDE: PyCharm

import os
import shutil
import re
from warnings import warn
from subprocess import check_output
import time


class FileOperation:
    def merge_dir(self, old_dst, new_dst, middle_path=''):
        """
        Move a directory to another directory
        :param old_dst: The directory to be moved
        :param new_dst: The directory to move to
        :param middle_path: neglect
        :return:
        """
        # determine whether if the old_dst is a directory or a file or not exists.
        if os.path.exists(old_dst):
            if os.path.isdir(old_dst):
                os.makedirs(new_dst, exist_ok=True)
                for ele in os.listdir(old_dst):
                    ele_path = os.path.join(old_dst, ele)
                    joined_middle_path = os.path.join(middle_path, ele)
                    self.merge_dir(ele_path, new_dst, middle_path=joined_middle_path)
            elif os.path.isfile(old_dst):
                new_dst_path = os.path.join(new_dst, middle_path)
                os.makedirs(os.path.split(new_dst_path)[0], exist_ok=True)
                shutil.move(old_dst, new_dst_path)
                return True
        else:
            return False

    def read_status(self, path=None, simulate=True):
        """
        Check the upload program status
        :param path: The path to call the upload program
        :param simulate: If True, the upload program will not be called.
        The result turns out to be True on defult
        :return: Boolean, True meaning that the upload program is ready to upload
        """
        if simulate:
            res ="""-------------- job stats ---------------
    ---------------- job stat ------------------
    JobName:local_test
    JobState:Running
    PendingTasks:0
    DispatchedTasks:0
    RunningTasks:0
    SucceedTasks:541
    FailedTasks:0
    ScanFinished:false
    RunningTasks Progress:
    ----------------------------------------
    """
            status = res
        else:
            res = check_output(['console', 'stat'], cwd=path, shell=True)
            status = res.decode()
        try:
            if 'no jobs is running' in status:
                return True
            JobStatus = re.compile('JobState:(.*?)\s').search(status).group(1)
            PendingTasks = int(re.compile('PendingTasks:(.*?)\s').search(status).group(1))
            RunningTasks = int(re.compile('RunningTasks:(.*?)\s').search(status).group(1))
            FailedTasks = int(re.compile('FailedTasks:(.*?)\s').search(status).group(1))
            DispatchedTasks = int(re.compile('DispatchedTasks:(.*?)\s').search(status).group(1))
        except AttributeError:
            time.sleep(1)
            return self.read_status(path)
        if PendingTasks == RunningTasks == FailedTasks == DispatchedTasks == 0 and JobStatus == 'Running':
            return True
        else:
            warn('The uploading program is not avaliable now')
            return False
