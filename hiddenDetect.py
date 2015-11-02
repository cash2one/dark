#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
import sys
import datetime
import os
from core.threads.threadManager import ThreadManager
from core.detect import Detect
from core.database.DBItem import detectResult, blacklist, whitelist, detectReport
from core.profile.profile import pf
from core.output.logging import logger
from core.output.console import consoleLog
from core.output.textFile import fileLog
from core.settings.settings import settings
from core.htmlfile.html import HtmlFile
from core.common import human_time
from core.utils.pkgenerator import PKgenerator

class hiddenlink_obj():
    def __init__(self, url, id):
        spider_path = pf.getProfileValue('spider', 'path')
        spider_setting_path = pf.getProfileValue('spider_setting', 'path')
        sys.path.append(spider_path)        # 将sinbot模块地址导入
        sys.path.append(spider_setting_path)# 将sinbot_settings模块的地址导入

        self.id = id                        # 用来保存当前检测链接对应数据库中的ID
        self.url = url                      # 用来保存当前检测的主页面的地址
        # self.rootPath = os.path.dirname(os.path.realpath(__file__)) # 用来保存当前检测的位置
        self.resultHiddenlink = {}          # 用来保存最终的检测结果
        self.urlList = []                   # 传递进来需要进行检测的URL列表
        self.curNum = 1                     # 统计当前检测的是第几条
        self.detectTM = ThreadManager()     # 线程管理

    def init(self):

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
        from settings.settings import settings as st # 引入sinbot_settings方法
        st.set('DEPTH_LIMIT', settings.getint('DEPTH_LIMIT'))    # 设置检测层数, 此处设置为2表示3层，从0开始计数
        reqList = sinbot_start(self.url)      # 开始爬取结果
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
        if len(hdDetect.hiddenSet):
            self.resultHiddenlink[url] = hdDetect.hiddenSet
        endtime = time.time()
        self.curNum += 1
        logger.info('One detect task finished! Using %f seconds!' % (endtime-starttime))

    def run(self):
        # 0. 设置检测的开始时间
        startTime = time.time()
        temp = time.localtime(startTime)
        self.strStartTime= time.strftime('%Y-%m-%d %H:%M:%S',temp)

        for url in self.urlList:
            url = url.strip('\n')      # 格式化传入的url，存在\n会导致产生浏览器访问失败
            if url is not None:
                args = (url, )
                self.detectTM.startTask(self.oneTask, args)
            else:
                logger.error('No url need to detect, please check it!')

        self.detectTM.join()
        # 2. 设置检测结束的时间
        endTime = time.time()
        self.interval = human_time(endTime - startTime)         # 设置检测用时

        # 3. 生成检测报告
        logger.info('Detect running success! Now will make the detect report file!')
        html_report = HtmlFile(self)
        try:
            report_path = html_report.genHtmlReport()
        except Exception, msg:
            logger.error('Make detect report file failed! Exception: %s.' % msg)

        logger.info('Store detect report success!')

        # 4. 将检测结果写入数据库
        threat_name = settings.get('THREAT_NAME')
        threat_sum = len(self.resultHiddenlink)
        threat_level = settings.get('THREAT_LEVEL')

        if report_path is None:
            logger.error('HTML maker get wrong report path! Please check it!')
            report_part_path = None
        else:
            path_list = report_path.split('/')
            report_part_path = path_list[-2] + '/' + path_list[-1]
        stat_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if threat_sum != 0:
            id = PKgenerator.getPrimaryKeyId()
            detectReport.store_url_hidden_report_in(id, self.id, threat_name, threat_level, threat_sum ,stat_time, report_part_path)

    def finsh(self):
        logger.info('Detect modules finished, now will be quit...')
        logger.info('Detect result: find %d url may have evil function!' % len(self.resultHiddenlink))
        # 关闭相关数据库的连接
        blacklist.end()
        whitelist.end()
        detectReport.end()
        detectResult.end()
        # 关闭日志模块
        logger.endLogging()

if __name__ == '__main__':
    url = 'http://www.baidu.com'
    hidden = hiddenlink_obj(url, 0)
    hidden.init()
    hidden.run()
    hidden.finsh()

