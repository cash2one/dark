#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
from core.threads.threadManager import ThreadManager
from core.detect import Detect

class hiddenlink_obj():
    def __init__(self, urlList):
        self.resultHiddenlink = {}          # 用来保存最终的检测结果
        self.urlList = urlList              # 传递进来需要进行检测的URL列表
        self.curNum = 1                     # 统计当前检测的是第几条
        self.detectTM = ThreadManager()     # 线程管理

    def init(self):
        self.detectTM.setMaxThreads(10)     # 设置可以同时进行任务的个数

    def oneTask(self, url):
        print 'Now detect is running and detect url is : %s, this is %d urls' % (url, self.curNum)
        starttime = time.time()
        hdDetect = Detect(url)
        hdDetect.init_detect()
        hdDetect.evil_detect()
        hdDetect.print_hiddenlink_result()
        self.resultHiddenlink = dict(self.resultHiddenlink, **hdDetect.hiddenSet)
        endtime = time.time()
        self.curNum += 1
        print 'Finished detect, and task end, using %f seconds!' % (endtime-starttime)

    def run(self):
        for url in self.urlList:
            url = url.strip('\n')      # 格式化传入的url，存在\n会导致产生浏览器访问失败
            if url is not None:
                self.detectTM.startTask(self.oneTask(url))



if __name__ == '__main__':
    f = open('./core/url.txt', 'r')
    urlList = f.readlines()
    f.close()
    hidden = hiddenlink_obj(urlList)
    hidden.init()
    hidden.run()
    print hidden.resultHiddenlink

