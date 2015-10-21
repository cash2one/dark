# -*- coding: utf-8 -*-
'''
outputManager.py

Author: peta
Date: 20150806

定义输出管理器类。
'''
from core.factory.factory import factory

class OutputManager(object):
    '''
    这个类管理一个输出插件列表，当消息到来时通知每一个输出插件输出消息。
    '''
    
    def __init__(self):
        self._outputPluginInstanceList = []         # 输出插件实例列表
        self._outputPluginNameList = []             # 输出插件名字列表
        self._outputPluginsOptions = {}             # 输出插件配置选项名

    def setOutputPlugins(self, outputPluginNameList):
        '''
        设置输出插件名称和实例列表。
        '''
        self._outputPluginInstanceList = []
        self._outputPluginNameList = outputPluginNameList
        for pluginName in self._outputPluginNameList:
            self._addOutputPluginInstance(pluginName)

    def endOutputPlugins(self):
        '''
        关闭所有的输出插件，但保留console。
        '''
        for outputPluginInstance in self._outputPluginInstanceList:
            outputPluginInstance.end()

    def setOutputPluginsOptions(self, pluginName, pluginOptions):
        '''
        设置输出插件配置选项。
        '''
        self._outputPluginsOptions[pluginName] = pluginOptions
    
    def debug(self, message, newLine=True):
        '''
        给输出插件实例列表中的每一个插件发送一个debug消息。
        '''
        self._callOutputPluginAction('debug', message, newLine)

    def warning(self, message, newLine=True):
        '''
        给输出插件实例列表中的每一个插件发送一个warning消息。
        '''
        self._callOutputPluginAction('warning', message, newLine)
    
    def error(self, message, newLine=True):
        '''
        给输出插件实例列表中的每一个插件发送一个error消息。
        '''
        self._callOutputPluginAction('error', message, newLine)
    
    def running(self, message, newLine=True):
        '''
        给输出插件实例列表中的每一个插件发送一个running消息。
        '''
        self._callOutputPluginAction('console', message, newLine)

    def inform(self, message, newLine=True):
        '''
        给输出插件实例列表中的每一个插件发送一个inform消息。
        '''
        self._callOutputPluginAction('inform', message, newLine)

    def logHttp(self, request, response):
        '''
        发送request/response一对对象给每一个插件。
        
        @parameter request: An HttpRequest object
        @parameter response: An HttpResponse object
        '''
        for pluginInstance in self._outputPluginInstanceList:
            pluginInstance.logHttp(request, response)
    
    def _addOutputPluginInstance(self, outputPluginName):
        '''
        传入一个输出插件名字，创建一个输出插件实例对象，并添加到输出插件实例对象列表。
        '''
        # 实例化插件
        plugin = factory('core.output.plugins.' + outputPluginName)

        # 处理插件配置选项
        if outputPluginName in self._outputPluginsOptions.keys():
            plugin.setOptions(self._outputPluginsOptions[outputPluginName])

        self._outputPluginInstanceList.append(plugin)

    def _callOutputPluginAction(self, actionname, message, *params):
        '''
        调用插件实例对应的方法，输出消息。
        '''
        if isinstance(message, unicode):
            message = message.encode('utf-8', 'replace')
        for plugin in self._outputPluginInstanceList:
            getattr(plugin, actionname)(message, *params)

om = OutputManager()
