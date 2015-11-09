#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
factory.py

Author: peta
Date: 20150806

定义工厂函数。
'''

import sys
import traceback

from dark_core.exception.DarkException import DarkException
from i18n import _

def factory(moduleName, className=None, *args, **kwargs):
    '''
    这个函数创建模块中类的一个实例。

    @:parameter moduleName: 模块名称。
    @:parameter className: 模块定义的类名称。
    @:parameter *args: 位置参数，实例化具体类时传递给构造函数。
    @:parameter **kwargs: 关键字参数，实例化具体类时传递给构造函数。
    '''
    try:
        __import__(moduleName)
    except ImportError, ie:
        raise DarkException, _('There was an error while importing %(moduleName)s: "%(exception)s"') \
                % {'moduleName':moduleName, 'exception':str(ie)}
    else:
        if not className:
            # 模块定义的类与模块同名,首字母需大写
            className = moduleName.split('.')[-1].capitalize()
        try:
            aModule = sys.modules[moduleName]
            aClass = getattr(aModule, className)
        except:
            raise DarkException, _('The requested "%(moduleName)s" doesn\'t have a correct format') % + {'moduleName':moduleName}
        else:
            try:
                inst = aClass(*args, **kwargs)
            except Exception, e:
                raise DarkException, _('Failed to get an instance of "%(className)s".\r\n\
                                       Original exception: "%(exception)s".\r\n\
                                       Traceback for this error: "%(traceback)s".') \
                        % {'className':className, 'exception':str(e), 'traceback':str(traceback.format_exc())}
            return inst
