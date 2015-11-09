#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'jason'

import chardet
import sys
from dark_core.request import Requset
from dark_core.parser.urlParser import url_object

class rebot_obj():
    def __init__(self):
        self.url = 'http://top.chinaz.com/list.aspx?p=%d'
        self.curUrl = None
        self.pageNum = 1
        self.curRequest = None
        self.urlList = []

    def run(self):
        while self.pageNum < 300:
            self.curUrl = self.url % self.pageNum
            print self.curUrl
            self.curRequest = Requset(self.curUrl, 10)
            self.curRequest.run()
            doc = self.curRequest.get_doc()
            infoTag = doc.xpath("//div[@class='info']/h3/a")
            for info in infoTag:
                try:
                    domainTitle = info.text
                    url = info.get('href')
                    url = url.replace("/site_", "http://").replace(".html", "/")
                    domain = url_object(url).getRootDomain
                    self.urlList.append((domain, domainTitle))
                except Exception, e:
                    print 'parse_web.rebot_obj.run: %s' % e

            self.pageNum += 1

    def result(self):
        for url in self.urlList:
            print url




if __name__ == '__main__':
    rebot = rebot_obj()
    rebot.run()
    rebot.result()