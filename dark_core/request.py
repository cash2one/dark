#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
import requests
from requests.exceptions import ConnectionError, Timeout
from socket import timeout
from dark_core.exception.DarkException import DarkException
from dark_core.output.logging import logger
from lxml import html as HTML
from i18n import _

DEBUG = False


class Requset:
    def __init__(self, url, retry_times=3):

        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                          ' Chrome/32.0.1700.76 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate,sdch'
        }

        self.url = url

        self.retry_times = retry_times

        self.retry_http_code = ['500', '502', '503', '504', '400', '408']

        self.visitable = True

        self.html = None

    def run(self):

        starttime = time.time()
        retry_flag = True
        retry_times = 0
        while retry_flag and retry_times < self.retry_times:
            try:
                req = requests.get(self.url, headers=self.header, timeout=5)
                # print req.encoding
                if req.encoding == 'gb2312':
                    self.html = req.text
                else:
                    self.html = req.content
                if req.status_code not in self.retry_http_code:
                    retry_flag = False
                else:
                    retry_times += 1
            except ConnectionError:
                retry_times += 1
            except Timeout:
                retry_times += 1
            except timeout:
                retry_times += 1
            except Exception, e:
                logger.error('Request run exception an Exception, and type is %s' % type(e))
                retry_flag = False
        if retry_times >= self.retry_times:
            self.visitable = False
        endtime = time.time()
        logger.debug('Request run finished, using %f seconds' % (endtime - starttime))

    def get_text(self):
        return self.html

    # doc返回结果为None的几种情况：1. 当网络不可达； 2. 当网络可达但是获取的html内容为空； 3. 当解析doc抛出异常的时候
    def get_doc(self):
        text = self.get_text()
        if text is not None and len(text):
            try:
                doc = HTML.document_fromstring(text)
                return doc
            except Exception, e:
                raise DarkException, _('Requset can not get doc, Exception: %s' % e)
        return None

    def is_visiable(self):
        return self.visitable


if __name__ == '__main__':
    re = Requset('http://www.chinabank.com.cn/index/index.shtml', 3)
    re.run()
    print re.get_text()
    print re.get_doc()
