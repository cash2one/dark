#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
import sys
from dark_core.snapshot.snapshot import Snapshot
from dark_core.database.mysqlExec import *
from dark_core.parser.htmlParser import html_object
from dark_core.parser.urlParser import url_object
from dark_core.parser.contentParser import content_obj
from dark_core.exception.DarkException import DarkException
from dark_core.settings.settings import settings
from dark_core.output.logging import logger
from request import Requset
from checker import Checker
from i18n import _

reload(sys)
sys.setdefaultencoding('utf8')


def get_keylist_from_string(string):
    content = content_obj()
    return content.get_key_words_by_all(string, 3)


class Detect():
    def __init__(self, url):
        self.url = url                          # 本次检测的URL
        self.hiddenSet = {}                     # 初始化结果对象
        self.suspectedSet = []                  # 保存疑似暗链的对象
        self.htmlObj = html_object(url)         # 初始化解析模块
        self.checker = Checker(self.htmlObj)    # 初始化检测模块

        self._curRequest = None     # 当前要进行检测的可疑链接Request请求对象
        self._curTitle = None       # 当前要进行检测的可疑链接的title信息提取
        self._curKeys = None        # 当前要进行检测的可疑链接的meta中的keywords信息提取
        self._curInfor = None       # 当前要进行检测的可疑链接的meta中的information信息提取
        self._curContent = None     # 当前要进行检测的可疑链接的标签下的text内容提取

    '''
    描述： 初始化检测
    '''

    def init_detect(self):
        try:
            # 本次要检测的页面的标题
            self.title = self.htmlObj.get_html_title_by_doc(self.htmlObj.doc)
            # 本次要检测的meta关键字
            self.metaKeys = self.htmlObj.get_html_meta_keywords_by_doc(self.htmlObj.doc)
            # 本次要检测的meta的描述
            self.metaInfor = self.htmlObj.get_html_meta_information_by_doc(self.htmlObj.doc)
        except DarkException, msg:
            logger.error(msg)
    '''
    描述： 将检测到有疑似暗链行为的对象保存到疑似set中
    '''

    def insert_suspected_into_set(self, elementGroup, type):
        tempTuple = (elementGroup, type)
        self.suspectedSet.append(tempTuple)

    '''
    描述： 将检测的结果和描述属性存储到暗链set中
    '''

    def insert_hiddenlink_into_set(self, url, tuple):
        self.hiddenSet.setdefault(url)
        self.hiddenSet[url] = tuple

    '''
    描述： 将暗链结果打印出来
    '''

    def print_hiddenlink_result(self):
        for (k, v) in self.hiddenSet.items():
            # print u'%s is a hidden link, and the hidden type is %s!' %(k.get('href'), v)
            logger.info('Find--->link: %s, content: %s, level: %s, type: %s' % (k, v[0], v[1], v[2]))
        logger.info('Simple detect find %d urls may have problem!' % len(self.hiddenSet))

    '''
    描述：判断当前链接是否在白名单中
    '''

    def is_link_in_white_list(self, url):
        urlParser = url_object(url)
        try:
            return find_domain_from_whitelist(urlParser.getRootDomain)
        except DarkException, msg:
            logger.error(msg)
        return False

    '''
    描述： 判断当前链接是否是黑名单库中的关键字
    '''

    def is_link_in_black_list(self, content):
        try:
            contentKeys = get_keylist_from_string(content)
        except DarkException, msg:
            logger.error(msg)
        for content in contentKeys:
            try:
                if find_keyword_from_blacklist(content):
                    return True
                else:
                    continue
            except DarkException, msg:
                logger.error(msg)
        return False

    '''
    描述： 判断当前的链接中是否存在与当前检测链接相似，若相似，则返回False，表示不是暗链
    '''

    def is_link_similer_detected_url(self):

        def conbine_list_to_new_string(list):
            '''
            描述： 将list中的string合并为一个string
            @:parameter: list : 要进行合并的list
            :return 合并后的字符串
            '''
            try:
                result = ''.join(list)
                return result
            except Exception, e:
                raise DarkException, _('Conbine list filed! Please check it! Exception: %s' % e)
            return ''

        try:
            detectString = conbine_list_to_new_string([self._curContent, self._curTitle, self._curKeys, self._curInfor])
            curentString = conbine_list_to_new_string([self.title, self.metaKeys, self.metaInfor])
        except DarkException, msg:
            logger.error(msg)

        content = content_obj()
        try:
            rate = content.compair_string_by_cos(detectString, curentString)
        except DarkException, msg:
            logger.error(msg)
        if rate > 0.0:
            return True
        else:
            return False

    '''
    描述： 检测当前的元素的行为是否为hidden行为，如果是，则返回True
    '''

    def hidden_behavior_detect(self):
        aList = self.htmlObj.get_a_tag_link_list()          # 获取所有A标签下的链接

        starttime = time.time()                             # 标记开始时间

        def group_a_element(aList):
            '''
            描述： 该函数用来将A标签列表按层级进行分组，同一层级的为一组
            @:parameter: aList，要进行分组的list
            :return: 分组后的结果
            '''
            groupList = []
            while(len(aList)):
                item = aList[0]     # 提取当前列表中的第一个元素，因为上面有while的限定，所以保证进入循环至少有一个元素
                brother = self.htmlObj.get_all_brother_element(item, True)    # 将该元素的兄弟元素提取出来
                group = filter(lambda x: x in aList, brother)           # 从它的兄弟元素中提取在aList中的元素
                aList = filter(lambda x: x not in group, aList)         # 重新对aList赋值，此时已经剔除筛选过的元素
                groupList.append(group)     # 将分组后的小组加入结果list中
            return groupList

        checkList = group_a_element(aList)              # 获取分组后的检测list

        for group in checkList:
            if len(group):
                a = group[0]        # 提取当前分组中的第一个元素检测该组是否为疑似暗链组
                if self.checker.is_color_hidden(a):
                    self.insert_suspected_into_set(group, 'Color hidden')
                elif self.checker.is_font_size_hidden(a):
                    self.insert_suspected_into_set(group, 'Font size hidden')
                elif self.checker.is_line_height_hidden(a):
                    self.insert_suspected_into_set(group, 'Line height hidden')
                elif self.checker.is_position_top_hidden(a):
                    self.insert_suspected_into_set(group, 'Position top hidden')
                elif self.checker.is_position_left_hidden(a):
                    self.insert_suspected_into_set(group, 'Position left hidden')
                elif self.checker.is_text_indent_hidden(a):
                    self.insert_suspected_into_set(group, 'Text indent hidden')
                elif self.checker.is_marquee_value_hidden(a):
                    self.insert_suspected_into_set(group, 'Marquee value hidden')
                elif self.checker.is_visible_hidden(a):
                    self.insert_suspected_into_set(group, 'Visible hidden')
                elif self.checker.is_overflow_height_hidden(a):
                    self.insert_suspected_into_set(group, 'Overflow height hidden')
                elif self.checker.is_overflow_width_hidden(a):
                    self.insert_suspected_into_set(group, 'Overflow weight hidden')
                else:
                    pass        # 不存在暗链行为
            else:
                logger.error('Hidden behavior detect group may had empty group! Please check it!')
        endtime = time.time()
        logger.info('Finishing the suspected hiddenlink detect, total using %f seconds!' % (endtime - starttime))

    '''
    描述：执行检测过程
    '''

    def evil_detect(self):

        def get_random_elements(list, number):
            '''
            描述： 该函数完成从要检测的列表中随机取指定数目个元素出来
            @:parameter list:  要提取的list
            @:parameter number: 要提取的数目，不足的整个提取
            :return: 提取后的list
            '''
            randomList = []
            import random
            try:
                randomList = random.sample(list, number if len(list) > number else len(list))
            except Exception, e:
                logger.error('Evil detect get random element filed! Please check it! Exception: %s' % e)
            return randomList

        def formart_string(string):
            return string.strip().strip('\r\n')

        self.hidden_behavior_detect()

        if len(self.suspectedSet):
            # -1. 按组进行检测
            for tuple in self.suspectedSet:                  # 每个tuple格式如:([element1, element2, ...], type)
                suspectList = tuple[0]                       # 提取疑似对象的List
                suspectType = tuple[1]                       # 提取疑似对象的类型
                _needRetry = True                            # 是否需要再次随机检测标志，当该标志为True时候，重新随机
                _retryTimes = 0                              # 重试次数，当重试次数达到阈值时停止
                while _needRetry and _retryTimes < settings.getint('RETRY_TIMES_MAX'):
                    _retryTimes += 1                         # 每次重试执行重试次数+1
                    needToDetectList = get_random_elements(suspectList, settings.getint('RANDOM_NUM')) # 随机检测3个
                    _curFlag = True                              # 检测停止标志
                    _middleNum = 0                               # 检测到中等威胁的个数，若中等威胁的个数大于2个，则将检测标志置为false
                    _detectTime = 0                              # 检测次数，当随机检测中所有元素检测完毕，则停止检测
                    _unreachable = 0                             # 不可达的网页个数，当随机检测的所有元素不可达，则重新进行抽样检测
                    while _curFlag and _detectTime < len(needToDetectList):
                        for element in needToDetectList:
                            _curUrl = element.get('href')
                            self._curContent = formart_string(element.text) if element.text else ''   # 提取疑似对象的文本内容，存在则获取，不存在则置为空
                            logger.info('Start evil detect and url is: %s' % _curUrl)
                            # 0.对其根域名进行白名单检测，如果在白名单中，则pass
                            if self.is_link_in_white_list(_curUrl):
                                logger.info('Finishing evil detect, because it is in whitelist!')
                            else:
                                # 1.检测网页中的文本信息是否在黑名单中, 如果在黑名单中，则直接记录，如果不在，则继续判断
                                if self.is_link_in_black_list(self._curContent):
                                     logger.info('Finishing evil detect, find evil url, because it is in blacklist!')
                                     _curFlag = False
                                else:
                                    # 2. 判断网络是否可达，如果不可达，则标记为低
                                    self._curRequest = Requset(_curUrl)
                                    self._curRequest.run()
                                    if self._curRequest.visitable:
                                        try:
                                            doc = self._curRequest.get_doc()
                                        except DarkException, msg:
                                            logger.error(msg)
                                        try:
                                            self._curTitle = self.htmlObj.get_html_title_by_doc(doc)
                                            self._curKeys = self.htmlObj.get_html_meta_keywords_by_doc(doc)
                                            self._curInfor = self.htmlObj.get_html_meta_information_by_doc(doc)
                                        except DarkException, msg:
                                            logger.error(msg)
                                        logger.debug('>' * 100)
                                        output = "\r\n当前页面的主要信息： \r\n%s\r\n%s\r\n%s\r\n检测页面的主要信息：\r\n%s\r\n%s\r\n%s\r\n%s" \
                                                 % (self.title, self.metaKeys, self.metaInfor, \
                                                    self._curContent, self._curTitle, self._curKeys, self._curInfor)
                                        logger.debug(output)
                                        logger.debug('<' * 100)

                                        # 3. 判断链接是否为相似内容，如果不是，继续判断
                                        if not self.is_link_similer_detected_url():
                                            # 4.判断链接是否在黑名单库中，如果存在，则标记为高，否则不标记为中
                                            if self.is_link_in_black_list(self._curTitle) or \
                                                    self.is_link_in_black_list(self._curKeys) or \
                                                    self.is_link_in_black_list(self._curInfor):
                                                logger.info('Finishing evil detect, find evil url, because it is in blacklist!')
                                                _curFlag = False
                                            else:
                                                logger.info('Finishing evil detect, find suspect url, beacuse it is different from homepage!')
                                                _middleNum += 1
                                                if _middleNum > 2:
                                                    _curFlag = False
                                        else:
                                            logger.info('Finishing evil detect, because it is similar to homepage!')
                                    else:
                                        logger.info('Finishing evil detect, not find evil url, beacuse it is unreachable!')
                                        _unreachable += 1
                            _detectTime += 1

                        if _unreachable == len(needToDetectList):
                            _needRetry = True
                            logger.debug('Finishing this round of detect, but all random url unreachable, need to retry!')
                        else:
                            _needRetry = False

                 # 将检测结果中确定的元素组写入结果set中
                if _curFlag:
                    # 说明检测3次完毕，未检测到太多可疑的链接
                    pass
                elif _middleNum != len(needToDetectList) and _curFlag:
                    # 说明包含疑似的暗链太多，需提出，并标记等级中
                    for element in suspectList:
                        url = element.get('href')
                        typeTuple = (self._curContent, 'Middle', suspectType)
                        self.insert_hiddenlink_into_set(url, typeTuple)
                else:
                    # 说明包含暗链，可以确定，标记等级高
                    for element in suspectList:
                        url = element.get('href')
                        typeTuple = (self._curContent, 'High', suspectType)
                        self.insert_hiddenlink_into_set(url, typeTuple)
        self.store_detect_result()

    def store_detect_result(self):
        if len(self.hiddenSet):
            # 保存快照
            fileText = self.htmlObj.html
            try:
                sp = Snapshot(self.url)
                sp.store_snapshot(fileText)
            except DarkException, msg:
                logger.error(msg)
            # 将检测结果保存到数据库中
            for (k, v) in self.hiddenSet.items():
                try:
                    store_url_hidden_type_to_detect_info(self.url, k, v[0], v[1], v[2])
                except DarkException, msg:
                    logger.error(msg)
            logger.info('Finishing store detect result!')
        else:
            logger.info('No need to store detect result!')

if __name__ == '__main__':
    from dark_core.output.console import consoleLog
    logger.setOutputPlugin(consoleLog)
    url = 'http://www.kingboxs.com/index.php?case=archive&act=search'
    hdDetect = Detect(url)
    hdDetect.init_detect()
    hdDetect.evil_detect()
    hdDetect.print_hiddenlink_result()
    logger.endLogging()
