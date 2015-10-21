# -*- coding: utf-8 -*-
'''
configurable.py

Author: peta
Date: 20150805

定义Configurable类。
'''
from i18n import _

class Configurable(object):
    '''
    可配置接口，所有实现该接口的类必须实现以下两个方法。

    1. setOptions(optionsList)
    2. getOptions()
    '''
    def setOptions(self, optionList):
        '''
        设置配置选项。

        @param optionList: optionList object。
        @return: None。
        ''' 
        raise NotImplementedError, _('Configurable object is not implementing required method setOptions')
        

    def getOptions(self):
        '''
        获取配置选项。

        @return: optionList object。
        '''
        raise NotImplementedError, _('Configurable object is not implementing required method getOptions')
