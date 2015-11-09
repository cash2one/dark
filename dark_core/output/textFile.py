#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from dark_core.settings.settings import settings


class FileLog(object):
    def __init__(self):
        pass

    def set_file_name(self, name):
        self._file = open(name, "a")

    def output(self, args):
        '''
        描述： 输出方法，将要输出的信息封装后写入日志中
        @:parameter args: 要写入的信息
        :return:
        '''
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print_str = '[%s] %s: %s \n' % (time_str, args[0], args[1])
        self._file.write(print_str)

    def close(self):
        self._file.close()


fileLog = FileLog()
