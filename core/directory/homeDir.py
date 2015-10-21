# -*- coding: utf-8 -*-
'''
homeDir.py

Author: peta
Date: 20150708

定义创建获取dark home目录的函数。
'''
import user
import os
import shutil
import datetime

from core.directory.localDir import get_local_dir


HOME_DIR = os.path.join(user.home, 
                        '.dark'+str(os.getpid())
                        +str(datetime.datetime.now().microsecond))

def get_home_dir():
    '''
    返回HOME_DIR。

    @return: HOME_DIR。
    '''
    return HOME_DIR

def create_home_dir():
    '''
    创建home目录。

    @return: 成功True。
    '''
    homeDir = get_home_dir()
    if not os.path.exists(homeDir):
        try:
            os.makedirs(homeDir)
        except OSError:
            return False

    # webroot目录
    webroot = homeDir + os.path.sep + 'webroot'
    if not os.path.exists(webroot):
        try:
            os.makedirs(webroot)
        except OSError:
            return False

    # profile目录
    profilesPath = homeDir + os.path.sep + 'profiles'
    defaultProfilesPath = get_local_dir() + os.path.sep + 'profiles' + os.path.sep
    if not os.path.exists(profilesPath):
        try:
            shutil.copytree(defaultProfilesPath, profilesPath)
        except OSError:
            return False

    return True
