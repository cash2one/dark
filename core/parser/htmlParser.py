#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import re
import time
from core.parser.urlParser import url_object
from core.browser import MyBrowser
from core.request import Requset
from core.exception.DarkException import DarkException
from core.settings.settings import settings
from core.output.logging import logger
from lxml import html as HTML
from bs4 import BeautifulSoup
from i18n import _


class html_object():
    def __init__(self, url):
        self.url = url
        self.doc = None
        self.html = None
        try:
            self.root = url_object(url).getRootDomain
        except Exception, msg:
            logger.error('Html parser initialization filed, please check it! Exception: %s' % msg)

        try:
            self.doc = HTML.document_fromstring(self.get_detect_html)
        except Exception, msg:
            logger.error('Html parser initialization filed, please check it! Exception: %s' % msg)
        self.javaScripts = self.get_all_script_content()
        self.styles = self.get_all_script_content()

    @property
    def get_detect_html(self):
        '''
        描述： 通过浏览器获取当前页面的HTML内容
        '''
        try:
            import socket
            timeout = settings.getfloat('HTML_TIMEOUT')
            socket.setdefaulttimeout(timeout)
        except Exception, e:
            raise DarkException, _('Failed to import socket to set timeout. Exception: %(exception)s.' % {'exception': str(e)})

        browser = MyBrowser()
        starttime = time.time()
        try:
            browser.visit(self.url)
        except socket.timeout:
            # 超时记入日志Waring，但并不终止操作
            pass
        except Exception, e:
            raise DarkException, _('Failed to visit url by using browser. Exception: %(exception)s.' % {'exception': str(e)})

        endtime = time.time()
        logger.info('Splinter loading a url using %f seconds' % (endtime - starttime))
        try:
            html = browser.get_html()  # 获取到当前页面的源码，貌似下面的浏览器没捕获异常
            html = BeautifulSoup(html, 'lxml').prettify()       # 将获取到的HTML进行格式化
            self.html = html
        except Exception, e:
            raise DarkException, _('Failed to get html by using browser. Exception: %(exception)s.' % {'exception': str(e)})
            browser.close()
            return
        if not html:
            browser.close()
            return
        browser.close()  # 获取页面后关闭浏览器
        return html

    def get_html_title_by_doc(self, doc):
        if doc is not None:
            try:
                title = doc.xpath("/html/head/title/text()")
                if len(title):
                    return ''.join(title)
            except Exception, e:
                raise DarkException, _('Failed to get title by using xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return ''

    def get_html_meta_keywords_by_doc(self, doc):
        if doc is not None:
            try:
                metaKeywords = doc.xpath("/html/head/meta[@name='keywords']/@content")
                if len(metaKeywords):
                    return ''.join(metaKeywords)
            except Exception, e:
                raise DarkException, _('Failed to get meta keywords by using xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return ''

    def get_html_meta_information_by_doc(self, doc):
        if doc is not None:
            try:
                metaDescription = doc.xpath("/html/head/meta[@name='description']/@content")
                if len(metaDescription):
                    return ''.join(metaDescription)
            except Exception, e:
                raise DarkException, _('Failed to get meta information by using xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return ''

    @property
    def get_links_from_doc(self):
        '''
        描述： 将获取的html文件生成dom树结构，从dom树中提取所有的link， 手册中信息如下：
        This html.iterlinks method finds any link in an
        action, archive, background, cite, classid, codebase, data, href,
        longdesc, profile, src, usemap, dynsrc, or lowsrc attribute.
        :return: Object include (element, attribute, link, pos) attribute
        '''
        if self.doc is not None:
            try:
                self.doc.make_links_absolute(self.url)
                links = self.doc.iterlinks()
                return links
            except Exception, e:
                raise DarkException, _('Failed to get links by using lxml.iterlinks. Exception: %(exception)s.' % {'exception': str(e)})
        return []

    def get_a_tag_link_list(self):
        '''
        描述： 获取包含link的所有<a>标签下的非css链接
        '''
        aTagLinkList = []
        for link in self.get_links_from_doc:
            if link[0].tag == 'a' and 'href' in link[0].keys():
                href = link[0].get("href")
                # print 'href:%s' %href
                # 在上述的方法中已经将其中的链接转换为绝对路径
                if href.startswith("http") and not href.endswith("css"):
                    rootDomain = url_object(href).getRootDomain  # 获取每个链接的根域名
                    if rootDomain != self.root:
                        aTagLinkList.append(link[0])
        return aTagLinkList

    @property
    def get_link_tag_css_list(self):
        '''
        描述： 获取包含link的所有<link>标签下为css样式的链接
        '''
        linkTagCssList = []
        for link in self.get_links_from_doc:
            if link[0].tag == 'link' and link[0].get('rel') == 'stylesheet' \
                    and 'href' in link[0].keys():
                href = link[0].get("href")
                linkTagCssList.append(href)
        return linkTagCssList

    @property
    def get_style_content_in_dom_node(self):
        '''
        描述： 获取当面dom分支下的所有style內容
        '''
        styleContentList = []
        if self.doc is not None:
            try:
                styleNodeList = self.doc.xpath("//style")  # 选取所有的style不管它存在的位置在哪儿
                styleContentList.extend([node.text_content() for node in styleNodeList])
            except Exception, e:
                raise DarkException, _('Failed to get style by doc.xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return styleContentList

    @property
    def get_style_content_in_css(self):
        '''
        描述： 从css样式中获取style内容
        '''
        styleContentList = []
        for css in self.get_link_tag_css_list:
            request = Requset(css, 1)
            request.run()
            req = request.get_text()
            if req is not None:
                styleContentList.append(req)
        return styleContentList

    def get_all_style_content(self):
        '''
        描述： 获取当前html中的全部style内容
        '''
        styleContentList = self.get_style_content_in_dom_node
        styleContentList.extend(self.get_style_content_in_css)
        styleContentList = map(lambda style: style.strip(), styleContentList)
        return styleContentList

    @property
    def get_script_tag_js_list(self):
        '''
        描述： 获取包含script的所有<script>标签下为js样式的链接
        '''
        scriptTagJsList = []
        for link in self.get_links_from_doc:
            if link[0].tag == 'script' and 'src' in link[0].keys():
                src = link[0].get("src")
                if src.endswith('.js'):
                    scriptTagJsList.append(src)
        return scriptTagJsList

    @property
    def get_script_content_in_dom_node(self):
        '''
        描述： 获取当面dom分支下的所有script內容
        '''
        scriptContentList = []
        if self.doc is not None:
            try:
                scriptNodeList = self.doc.xpath("//script")
                scriptContentList.extend([node.text_content() for node in scriptNodeList])
            except Exception, e:
                raise DarkException, _('Failed to get script by doc.xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return scriptContentList

    @property
    def get_script_content_in_js(self):
        '''
        描述： 从js文件中获取script内容
        '''
        scriptContentList = []
        for js in self.get_script_tag_js_list:
            request = Requset(js, 1)
            request.run()
            req = request.get_text()
            if req is not None:
                scriptContentList.append(req)
        return scriptContentList

    def get_all_script_content(self):
        '''
        描述： 获取当前html中的全部style内容
        '''
        scriptContentList = self.get_script_content_in_dom_node
        scriptContentList.extend(self.get_script_content_in_js)
        scriptContentList = map(lambda script: script.strip(), scriptContentList)
        return scriptContentList

    def get_all_brother_element(self, element, includeSelf=True):
        '''
        描述： 获取当前页面中某个元素的所有兄弟元素， 如过includeSelf标志为Ture，则表示包含当前元素
        '''
        brotherList = []
        parent = element.getparent()
        if parent is not None:
            brotherList = parent.getchildren()
            if includeSelf:
                pass
            else:
                brotherList.remove(element)
        else:
            if includeSelf:
                brotherList.append(element)
            else:
                pass
        return brotherList

    def get_all_parent_element(self, element):
        '''
        描述： 获取当前页面中某个元素的所有祖先元素
        '''

        parentList = []
        while element is not None:
            parent = element.getparent()
            if (parent is not None) and parent.tag != 'html':
                # print 'get_all_parent_element :' + parent.tag
                parentList.append(parent)
            element = parent
        return parentList

    def get_all_child_element(self, element):
        '''
        描述： 获取当前页面中某个元素的所有后代元素
        '''
        return element.getchildren()

    def print_element(self, element):
        '''
        描述： 打印当前页面中某个元素的信息
        '''
        keys = element.keys()
        string = '<%s' % element.tag
        for key in keys:
            string += ' %s=' % key
            string += element.get(key)
        string += '>'
        text = element.text
        if text is not None:
            string += text
        else:
            string += '...'
        string += '<\%s>' % element.tag
        return string

    def get_element_style_attr_value(self, element, attrString):
        '''
        描述： 提取某个元素中某个样式的值
        '''
        keys = element.keys()
        style = None
        """
        <div style="position: absolute; top: -999px;left: -999px;">
        print element.tag + '\t' + element.get(keyString)
        """
        if 'style' in keys:
            style = element.get('style')
        elif 'class' in keys:
            style = self.get_style_in_class(element.get('class'))
        if style is not None:
            match = re.search(r'%s\s*:\s*[#]?([^;>]+)' % attrString,
                              style, re.IGNORECASE)
            if match is not None:
                # print u'tag: ' + element.tag + '-->' + u'string: ' + match.group(0)
                # print match.group(1)
                return match.group(1)
            else:
                return
        else:
            return

    def get_id_in_javascript(self, functionName):
        '''
        描述： 获取html中的javascript方法中的ID
        '''
        matchList = []
        for js in self.javaScripts:
            try:
                blockRegex = r'function\s+%s\(\).+?document.getElementById\([\'\"](\w+)[\'\"]\).+?\}' % functionName
                block = re.search(blockRegex, js, re.IGNORECASE | re.DOTALL)
                if block is not None:
                    searchRegex = r'document.getElementById\([\'\"](\w+)[\'\"]\)'
                    match = re.findall(searchRegex, block.group(0), re.IGNORECASE | re.DOTALL)
                    if match is not None:
                        matchList = match
            except Exception, msg:
                logger.error(msg)
        return matchList

    def get_style_in_class(self, className):
        '''
        描述： 获取html中的class对应的style
        '''
        for script in self.styles:
            try:
                match = re.search(r'%s\x20[^\{]*\{([^\}]+)\}' % className, script, re.IGNORECASE | re.DOTALL)
                if match is not None:
                    return match.group(1)
            except Exception, msg:
                logger.error(msg)
        return None


if __name__ == '__main__':
    from core.output.console import consoleLog
    logger.setOutputPlugin(consoleLog)
    url = "http://www.dtzwdt.gov.cn/"
    htObj = html_object(url)
    print htObj.get_detect_html
    # htObj.set_paresr_doc()

    # aList = htObj.get_a_tag_link_list()

    '''
    styleList = htObj.get_all_style_content()  # 获取所有的非style属性下的样式
    for style in styleList:
        print style

    print '____________________________'

    scriptList = htObj.get_all_script_content()  # 获取当前页面中的所有javascript
    for script in scriptList:
        print script
    '''
