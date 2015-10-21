# -*- coding: utf-8 -*-
'''
option.py

Author: peta
Date: 20150805

定义配置选项类。
'''
import re
import copy

from core.exception.DarkException import DarkException
from core.http.data.urlobject import UrlObject
from i18n import _


class Option:
    '''
    配置选项类。
    '''
    BOOL = 'boolean'
    INT = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    URL = 'url'
    IPPORT = 'ipport'
    LIST = 'list'
    REGEX = 'regex'
    
    def __init__(self, name, value, type):
        '''
        @parameter name: 配置选项名称。
        @parameter value: 配置选项值。
        @parameter type: 配置选项类型，如boolean, integer, string, etc..
        '''
        self.name = name
        self._value = value
        self.type = type

    @property
    def strValue(self):
        return self._getStr(self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        '''
        value setter。

        @parameter value: 'True' or 'a,b,c'
        '''
        try:
            if self.type == 'integer':
                res = int(value)
            elif self.type == 'float':
                res = float(value)
            elif self.type == 'boolean':
                if value.lower() == 'true':
                    res = True
                else:
                    res = False
            elif self.type == 'list':
                res = []
                value += ','
                tmp = re.findall('(".*?"|\'.*?\'|.*?),', value, re.U)
                if tmp:
                    tmp = [y.strip() for y in tmp if y != '']
                    for u in tmp:
                        if (u.startswith('"') and u.endswith('"')) or (u.startswith("'") and u.endswith("'")):
                            res.append(u[1:-1])
                        else:
                            res.append(u)

                else:
                    raise ValueError
            elif self.type == 'string':
                res = str(value)
            elif self.type == 'url':
                try:
                    res = UrlObject(value)
                except Exception, e:
                    msg = str(e)
                    raise DarkException(msg)
            elif self.type == 'regex':
                try:
                    re.compile(value)
                except:
                    raise DarkException, _('The regular expression "%(value)s" is invalid!') % {'value':value}
                else:
                    res = value
            else:
                raise DarkException, _('Unknown type: %(type)s') % {'type':self.type}
        except ValueError:
            raise DarkException, _('The value "%(value)s" cannot be casted to "%(type)s"') % (value, self._type)
        else:
            self._value = res
        
    def _getStr(self, value):
        if isinstance(value, type([])):
            return ','.join([str(i) for i in value])
        else:
            return str(value)

    def __repr__(self):
        '''
        Python表示。        
        '''
        fmt = '<option name:%s|type:%s|value:%s>'
        return fmt % (self.name, self.type, self.strValue)
    
    def __eq__(self, other):
        if not isinstance(other, Option):
            return False
        
        name = self.name == other.name
        type = self.type == other.type
        value = self.value == other.value
        return name and type and value 
        
    def copy(self):
        '''
        深拷贝。
        '''
        return copy.deepcopy(self)
