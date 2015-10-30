#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from core.exception.DarkException import DarkException
from i18n import _
import os


def human_time(time):
    try:
        time = int(time)
    except Exception, e:
        raise DarkException, _('Convert time to int filed! Please check it! Exception: %s' % e)
    hour = time / 3600
    minute = time % 3600 / 60
    second = time % 60
    str_time = u'%s小时%s分%s秒' % (hour, minute, second)
    return str_time
