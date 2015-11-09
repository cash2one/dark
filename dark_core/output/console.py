#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class ConsoleLog(object):
    def __init__(self):
        pass

    def output(self, args):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print '[%s] %s: %s' % (time_str, args[0], args[1])

    def close(self):
        pass


consoleLog = ConsoleLog()
