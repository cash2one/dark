#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
localDir.py

Author: peta
Date: 20150708

定义获取dark local目录的函数。
'''
import os

DARK_LOCAL_DIR = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])


def get_local_dir():
    '''
    返回dark_LOCAL_DIR。

    @return: DARK_LOCAL_DIR
    '''
    return DARK_LOCAL_DIR


if __name__ == '__main__':
    print get_local_dir()
