#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from splinter import Browser

BROWSER_TYPE = 'phantomjs'
DEBUG = True


class MyBrowser:
    """
    This class is a browser class, which can setting your browser type
    """

    def __init__(self):
        self.browser = Browser(BROWSER_TYPE)
        if DEBUG:
            print 'Splinter browser is init, and the browser type is %s!' % BROWSER_TYPE

    def close(self):
        self.browser.quit()
        if DEBUG:
            print 'Splinter browser is close success!'

    def visit(self, url):
        if DEBUG:
            print 'Splinter browser is visiting a url!'
        self.browser.visit(url)

    def get_html(self):
        return self.browser.html

    def get_title(self):
        return self.browser.title

    def reload(self):
        self.browser.reload()
        if DEBUG:
            print 'Splinter browser is reloading a url!'


if __name__ == '__main__':
    MyBrowser = Browser()
    MyBrowser.visit('http://www.baidu.com')
    print MyBrowser.get_title()
    MyBrowser.close()
