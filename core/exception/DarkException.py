#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

'''
描述： 定义各类异常的状况
'''


class DarkException(Exception):
    """
    描述： darkException类型异常
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = str(value)

    def __str__(self):
        return self.value


class DarkManagerException(Exception):
    """
    描述： DarkManagerException类型异常，该类异常的引起原因为某个管理类中的某个方法抛出异常
    """

    def __init__(self, value):
        Exception.__init__(self)
        self.value = str(value)

    def __str__(self):
        return self.value


class DarkMustStopException(Exception):
    """
    描述： DarkMustStopException类型异常，该类异常的引起后必须停止运行。
    """

    def __init__(self, msg, errs=()):
        self.msg = str(msg)
        self.errs = errs

    def __str__(self):
        return str(self.msg) + '\n'.join([str(e) for e in self.errs])

    __repr__ = __str__


class DarkMustStopByKnownReasonException(DarkMustStopException):
    """
    描述： DarkMustStopByKnownReasonException类型异常，该类异常的引起后必须停止运行, 但异常原因可知。
    """
    def __init__(self, msg, errs=(), reason=None):
        DarkMustStopException.__init__(self, msg, errs)
        self.reason = reason

    def __str__(self):
        _str = DarkMustStopException.__str__(self)
        if self.reason:
            _str += ' - Reason: %s' % self.reason
        return _str
