#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import time
import sys
from core.snapshot.snapshot import sp
from core.database.DBItem import blacklist, whitelist, detectResult
from core.parser.htmlParser import html_object
from core.parser.urlParser import url_object
from core.parser.contentParser import content_obj
from core.exception.DarkException import DarkException
from core.output.logging import logger
from request import Requset
from checker import Checker

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

    def insert_suspected_into_set(self, element, type):
        self.suspectedSet.append((element, type))

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
            logger.info('Find--->link: %s level: %s type: %s' % (k, v[0], v[1]))
        logger.info('Simple detect find %d urls may have problem!' % len(self.hiddenSet))

    '''
    描述： 将要检测是否存在暗链的对象进行分组，减少检测次数
    '''

    def get_detection_object(self, elements):
        for element in elements:
            brotherList = self.htmlObj.get_all_brother_element(element, False)
            for brother in brotherList:
                if brother in elements:
                    elements.remove(brother)
                    # print 'remove: ' + brother.get('href') + ' in %s group!'%element.get('href')
        return elements

    '''
    描述：判断当前链接是否在白名单中
    '''

    def is_link_in_white_list(self, url):
        urlParser = url_object(url)
        return whitelist.find_url_in(urlParser.getRootDomain)

    '''
    描述： 判断当前链接是否是黑名单库中的关键字
    '''

    def is_link_in_black_list(self):
        try:
            contentKeys = get_keylist_from_string(self._curContent)
            titleKeys = get_keylist_from_string(self._curTitle)
            keyKeys = get_keylist_from_string(self._curKeys)
            inforKeys = get_keylist_from_string(self._curInfor)
        except DarkException, msg:
            logger.error(msg)
        if blacklist.find_keyword_in(contentKeys):
            return True
        elif blacklist.find_keyword_in(titleKeys):
            return True
        elif blacklist.find_keyword_in(keyKeys):
            return True
        elif blacklist.find_keyword_in(inforKeys):
            return True
        else:
            return False

    '''
    描述： 判断当前的链接中是否存在与当前检测链接相似，若相似，则返回False，表示不是暗链
    '''

    def is_link_similer_detected_url(self):

        def conbine_list_to_new_string(list):
            result = ''
            for item in list:
                if item is not None:
                    result += item
            return result

        detectString = conbine_list_to_new_string([self._curContent, self._curTitle, self._curKeys, self._curInfor])
        curentString = conbine_list_to_new_string([self.title, self.metaKeys, self.metaInfor])
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
        aList = self.htmlObj.get_a_tag_link_list()
        starttime = time.time()
        for a in aList:
            # print a.get('href')
            if self.checker.is_color_hidden(a):
                self.insert_suspected_into_set(a, 'Color hidden')
            elif self.checker.is_font_size_hidden(a):
                self.insert_suspected_into_set(a, 'Font size hidden')
            elif self.checker.is_line_height_hidden(a):
                self.insert_suspected_into_set(a, 'Line height hidden')
            elif self.checker.is_position_top_hidden(a):
                self.insert_suspected_into_set(a, 'Position top hidden')
            elif self.checker.is_position_left_hidden(a):
                self.insert_suspected_into_set(a, 'Position left hidden')
            elif self.checker.is_text_indent_hidden(a):
                self.insert_suspected_into_set(a, 'Text indent hidden')
            elif self.checker.is_marquee_value_hidden(a):
                self.insert_suspected_into_set(a, 'Marquee value hidden')
            elif self.checker.is_visible_hidden(a):
                self.insert_suspected_into_set(a, 'Visible hidden')
            elif self.checker.is_overflow_height_hidden(a):
                self.insert_suspected_into_set(a, 'Overflow height hidden')
            elif self.checker.is_overflow_width_hidden(a):
                self.insert_suspected_into_set(a, 'Overflow weight hidden')
            else:
                pass
        endtime = time.time()
        logger.info('Finishing the suspected hiddenlink detect, total using %f seconds!' % (endtime - starttime))

    '''
    描述：执行检测过程
    '''

    def evil_detect(self):
        self.hidden_behavior_detect()
        if len(self.suspectedSet):
            for tuple in self.suspectedSet:
                suspectUrl = tuple[0].get('href')
                suspectType = tuple[1]
                logger.info('Start evil detect and url is: %s' % suspectUrl)

                # 0.设定当前的Request对象
                self._curRequest = Requset(suspectUrl)
                # 1.对其根域名进行白名单检测，如果在白名单中，则pass
                if self.is_link_in_white_list(suspectUrl):
                    logger.info('Finishing evil detect, because it in whitelist!')
                else:
                    # 2. 判断网络是否可达，如果不可达，则标记为低
                    self._curRequest.run()
                    if self._curRequest.visitable:
                        try:
                            doc = self._curRequest.get_doc()
                        except DarkException, msg:
                            logger.error(msg)
                        self._curContent = tuple[0].text if tuple[0].text else ''
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
                            if self.is_link_in_black_list():
                                logger.info('Finishing evil detect, and add it into level: heigh!')
                                typeTuple = ('heigh', suspectType)
                                self.insert_hiddenlink_into_set(suspectUrl, typeTuple)
                            else:
                                typeTuple = ('middle', suspectType)
                                logger.info('Finishing evil detect, and add it into level: middle!')
                                self.insert_hiddenlink_into_set(suspectUrl, typeTuple)
                        else:
                            logger.info('Finishing evil detect, because they are similar!')
                    else:
                        typeTuple = ('low', suspectType)
                        logger.info('Finishing evil detect, and add it into level: low!')
                        self.insert_hiddenlink_into_set(suspectUrl, typeTuple)
        self.store_detect() 

    def store_detect(self):
        if len(self.hiddenSet):
            # 保存快照
            fileName = self.url.strip('http://')
            fileText = self.htmlObj.html
            try:
                sp.store_snapshot(fileName, fileText)
            except DarkException, msg:
                logger.error(msg)
            # 将检测结果保存到数据库中
            for (k, v) in self.hiddenSet.items():
                detectResult.store_url_hidden_type_in(self.url, k, v[0], v[1])

            logger.info('Finishing store detect result!')
        else:
            logger.info('No need to store detect result!')


if __name__ == '__main__':
    url = 'http://www.shenguang.com'
    hdDetect = Detect(url)
    hdDetect.init_detect()

    print u'<-------开始分析-------->'
    hdDetect.evil_detect()
    print u'<-------打印结果-------->'
    hdDetect.print_hiddenlink_result()
    print hdDetect.suspectedSet
    print u'<----------------------->'
