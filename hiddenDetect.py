#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
import sys
from core.threads.threadManager import ThreadManager
from core.detect import Detect
from core.database.DBItem import detectResult, blacklist, whitelist
from core.profile.profile import pf
from core.output.logging import logger
from core.output.console import consoleLog
from core.output.textFile import fileLog
from core.snapshot.snapshot import sp

class hiddenlink_obj():
    def __init__(self):
        spider_path = pf.getProfileValue('spider', 'path')
        spider_setting_path = pf.getProfileValue('spider_setting', 'path')
        sys.path.append(spider_path)        # 将sinbot模块地址导入
        sys.path.append(spider_setting_path)# 将sinbot_settings模块的地址导入

        self.resultHiddenlink = {}          # 用来保存最终的检测结果
        self.urlList = []                   # 传递进来需要进行检测的URL列表
        self.curNum = 1                     # 统计当前检测的是第几条
        self.detectTM = ThreadManager()     # 线程管理

    def init(self, target):

        def get_url(list):
            '''
            描述： 将爬虫获取到的request列表中的url提取出来，并且格式化与去重复
            :param list:
            :return:
            '''
            tempList = []
            for item in list:
                url = item.url
                if url and url[-1] == '/':
                    url = url[:-1]
                tempList.append(url)
            return set(tempList)

        self.detectTM.setMaxThreads(10)     # 设置可以同时进行任务的个数

        from sinbot import sinbot_start     # 引入sinbot_start方法
        from settings.settings import settings  # 引入sinbot_settings方法
        settings.set('DEPTH_LIMIT', '3')    # 设置检测层数
        reqList = sinbot_start(target)      # 开始爬取结果
        self.urlList = get_url(reqList)    # 将爬取到的url结果保存到列表中

        if pf.getLogType() == 'True':
            logger.setOutputPlugin(fileLog)
        else:
            logger.setOutputPlugin(consoleLog)
        logger.info('Detect modules complete initialization...')

    def oneTask(self, url):
        logger.info('One detect task is running(%d/%d), detect url is : %s' % (self.curNum, len(self.urlList), url))
        starttime = time.time()
        hdDetect = Detect(url)
        hdDetect.init_detect()
        hdDetect.evil_detect()
        hdDetect.print_hiddenlink_result()
        self.resultHiddenlink = dict(self.resultHiddenlink, **hdDetect.hiddenSet)
        endtime = time.time()
        self.curNum += 1
        logger.info('One detect task finished! Using %f seconds!' % (endtime-starttime))

    def run(self):
        for url in self.urlList:
            url = url.strip('\n')      # 格式化传入的url，存在\n会导致产生浏览器访问失败
            if url is not None:
                self.detectTM.startTask(self.oneTask(url))
            else:
                logger.error('No url need to detect, please check it!')

    def finsh(self):
        logger.info('Detect modules finished, now will be quit...')
        # 关闭相关数据库的连接
        blacklist.end()
        whitelist.end()
        detectResult.end()
        # 关闭日志模块
        logger.endLogging()

if __name__ == '__main__':
    hidden = hiddenlink_obj()
    hidden.init('http://www.kingboxs.com')
    hidden.run()
    hidden.finsh()

