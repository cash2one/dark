# -*- coding: utf-8 -*-
'''
primaryKeyGenerator.py

primaryKeyGenerator模块用于生成主键ID。
'''

import datetime
import random

class PKgenerator(object):
    '''
    主键生成器，用于生成数据表主键ID。
    '''
    
    @classmethod
    def getPrimaryKeyId(cls):
        return object.__new__(cls)._createKeyId()

    def _getCurrentDateTime(self):
        '''
        获取当前时间，精确到3位毫秒，格式 YYYYmmddHHMMSSmmm(Python只能精确到毫秒级)。
        
        @return: 格式化时间字符串
        '''
        
        curTime = datetime.datetime.now()  
        return curTime.strftime('%Y%m%d%H%M%S') + str(curTime.microsecond)[:3]
  
    def _createKeyId(self):
        '''
        生成数据库主键ID值。
        
        @return: 22位ID字符串
        '''
        
        return self._getCurrentDateTime() + str(random.randrange(10000, 99999))
