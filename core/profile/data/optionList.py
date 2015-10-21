# -*- coding: utf-8 -*-
'''
optionList.py

Author: peta
Date: 20150805

定义配置选项列表类。
'''
from core.exception.DarkException import DarkException
from i18n import _

class OptionList(object):
    '''
    配置选项列表类。
    '''
    def __init__(self):
        self._oList = []
        
    def add(self, option):
        self._oList.append(option)
    append = add
    
    def __len__(self):
        return len(self._oList)
    
    def __repr__(self):
        return '<optionList: '+ '|'.join([i.name for i in self._oList]) +'>'

    def __eq__(self, other):
        if not isinstance(other, OptionList):
            return False
        
        return self._oList == other._oList
        
    def __contains__(self, itemName):
        for o in self._oList:
            if o.name == itemName:
                return True
        return False
    
    def __getitem__(self, itemName):
        '''
        根据配置选项名称从配置选项列表中获取配置选项。
        
        def setOptions(self, optionsList):
            self._xxx = optionsList['xxx']
            
        @return: option object。
        '''
        try:
            item_name = int(itemName)
        except:
            # A string
            for o in self._oList:
                if o.name == itemName:
                    return o
            raise DarkException, _('The optionList object doesn\'t contain an option with the name: %(name)s') % {'name':itemName}
        else:
            # An integer
            return self._oList[item_name]
