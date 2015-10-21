# -*- coding: utf-8 -*-
'''
i18n.py

Author: peta
Date: 20150706

定义国际化方法。
'''
import os
import gettext


APP_NAME = 'dark'
LOCALE_DIR = os.path.abspath('locale')
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = '/usr/share/locale'
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext
