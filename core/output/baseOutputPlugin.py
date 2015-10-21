# -*- coding: utf-8 -*-
'''
baseOutputPlugin.py

Author: peta
Date: 20150806

定义输出插件基类。
'''
import time
import string

from core.profile.data.configurable import Configurable


class BaseOutputPlugin(Configurable):
    '''
    输出插件基类。
    '''
    def end(self):
        '''
        当不再使用的时调用此方法进行插件收尾工作。
        '''
        pass

    def debug(self, message, newLine=True):
        '''
        当需要输出调试信息时调用此方法。
        '''
        pass

    def warning(self, message, newLine=True):
        '''
        当需要输出警告信息时调用此方法。
        '''
        pass

    def error(self, message, newLine=True):
        '''
        当需要输出错误信息时调用此方法。
        '''
        pass

    def running(self, message, newLine=True):
        '''
        当需要输出运行信息时调用此方法。
        '''
        pass

    def inform(self, message, newLine=True):
        '''
        当需要输出通知信息时调用此方法。
        '''
        pass

    def logHttp(self, request, response):
        '''
        记录HTTP请求/响应。
        '''
        pass

    def getOptions(self):
        '''
        这两个类是Configurable中必须要实现的类
        '''
        pass

    def setOptions(self, optionList):
        '''
        这两个类是Configurable中必须要实现的类
        '''
        pass

    def _makePrintable(self, aString):
        aString = str(aString)
        return ''.join(ch for ch in aString if ch in string.printable)

    def _formatMsg(self, msg, type):
        now = time.localtime(time.time())
        thetime = time.strftime('%c', now)
        timestamp = '[%s - ]' % thetime + type + ']'
        msg = timestamp + '%s' % msg
        return msg
