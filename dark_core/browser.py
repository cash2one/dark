#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from splinter import Browser
from dark_core.settings.settings import settings
from dark_core.output.logging import logger

DEBUG = True


class MyBrowser:
    """
    This class is a browser class, which can setting your browser type
    """

    def __init__(self):
        self.browser = Browser(settings.get('BROWSER_TYPE'))
        logger.info('Splinter browser is init!')

    def close(self):
        self.browser.quit()
        logger.info('Splinter browser is close success!')

    def visit(self, url):
        self.browser.visit(url)
        logger.info('Splinter browser is visiting : %s' % url)

    def get_html(self):
        return self.browser.html

    def get_title(self):
        return self.browser.title

    def reload(self):
        self.browser.reload()


if __name__ == '__main__':
    MyBrowser = Browser()
    MyBrowser.visit('http://www.baidu.com')
    print MyBrowser.get_title()
    MyBrowser.close()
