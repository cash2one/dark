# -*- coding: utf-8 -*-
'''
config.py

Author: peta
Date: 20150805

定义保存全局配置选项字典对象cf。
'''

class Config(dict):
    '''
    全局保存配置选项类。
    '''
        
    def save(self, variableName, value):
        '''
        保存配置选项信息。
        '''
        self[variableName] = value
        
    def getData(self, variableName, default=None):
        '''
        返回variableName对应的value。
        '''
        return self.get(variableName, default)
    
    def cleanup(self):
        '''
        清空字典。
        '''
        self.clear()    
        
cf = Config()
