#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from lxml import html as HTML
import re
import time

from core.parser.urlParser import url_object
from core.browser import MyBrowser
from core.request import Requset
from core.exception.DarkException import DarkException
from core.settings.settings import settings
from i18n import _

class html_object:
    def __init__(self, url):

        self.url = url
        self.doc = None
        try:
            self.root = url_object(url).getRootDomain
        except Exception, e:
            raise DarkException, _('Failed to get root by url_object in html_object init. Exception: %(exception)s.' % {'exception': str(e)})

        try:
            self.doc = HTML.document_fromstring(self.get_detect_html)
        except Exception, e:
            raise DarkException, _('Failed to get doc by html in html_object init. Exception: %(exception)s.' % {'exception': str(e)})
        self.javaScripts = self.get_all_script_content()
        self.styles = self.get_all_script_content()

    '''
    描述： 通过浏览器获取当前页面的HTML内容
    '''

    @property
    def get_detect_html(self):

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
        print '-'*20,
        print ' Splinter loading time: %f' % (endtime-starttime),
        print '-'*20
        try:
            html = browser.get_html()  # 获取到当前页面的源码，貌似下面的浏览器没捕获异常
            #print html
        except Exception, e:
            print 'htmlParser.html_object.get_detect_html.browser.get_html: %s' % e
            browser.close()
            return
        if not html:
            browser.close()
            return
        browser.close()    # 获取页面后关闭浏览器
        return html


    def get_html_title_by_doc(self, doc):
        if doc is not None:
            try:
                title = doc.xpath("/html/head/title/text()")
                if len(title):
                    return title[0]
            except Exception, e:
                print 'htmlParser.html_obj.get_html_title_by_doc: %s' % e
        return ''

    def get_html_meta_keywords_by_doc(self, doc):
        if doc is not None:
            try:
                metaKeywords = doc.xpath("/html/head/meta[@name='keywords']/@content")
                if len(metaKeywords):
                    return metaKeywords[0]
            except Exception, e:
                print 'htmlParser.html_obj.get_html_meta_keywords_by_doc: %s' % e
        return ''

    def get_html_meta_information_by_doc(self, doc):
        if doc is not None:
            try:
                metaDescription = doc.xpath("/html/head/meta[@name='description']/@content")
                if len(metaDescription):
                    return metaDescription[0]
            except Exception, e:
                print 'htmlParser.html_obj.get_html_meta_information_by_doc: %s' % e
        return ''


    '''
    描述： 将获取的html文件生成dom树结构，从dom树中提取所有的link
    '''

    @property
    def get_links_from_doc(self):
        """
        This html.iterlinks method finds any link in an
        action, archive, background, cite, classid, codebase, data, href,
        longdesc, profile, src, usemap, dynsrc, or lowsrc attribute.
        :return: Object include (element, attribute, link, pos) attribute
        """
        if self.doc is not None:
            try:
                self.doc.make_links_absolute(self.url)
                links = self.doc.iterlinks()
                return links
            except Exception, e:
                print 'htmlParser.html_object.get_links_from_doc: %s' % e
        return []

    '''
    描述： 获取包含link的所有<a>标签下的非css链接
    '''

    def get_a_tag_link_list(self):
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

    '''
    描述： 获取包含link的所有<link>标签下为css样式的链接
    '''

    @property
    def get_link_tag_css_list(self):
        linkTagCssList = []
        for link in self.get_links_from_doc:
            if link[0].tag == 'link' and link[0].get('rel') == 'stylesheet' \
                    and 'href' in link[0].keys():
                href = link[0].get("href")
                linkTagCssList.append(href)
        return linkTagCssList

    '''
    描述： 获取当面dom分支下的所有style內容
    '''

    @property
    def get_style_content_in_dom_node(self):
        styleContentList = []
        if self.doc is not None:
            try:
                styleNodeList = self.doc.xpath("//style")  # 选取所有的style不管它存在的位置在哪儿
                styleContentList.extend([node.text_content() for node in styleNodeList])
            except Exception, e:
                raise DarkException, _('Failed to get style by doc.xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return styleContentList

    '''
    描述： 从css样式中获取style内容
    '''

    @property
    def get_style_content_in_css(self):
        styleContentList = []
        for css in self.get_link_tag_css_list:
            request = Requset(css, 1)
            request.run()
            req = request.get_text()
            if req is not None:
                styleContentList.append(req)
        return styleContentList

    '''
    描述： 获取当前html中的全部style内容
    '''

    def get_all_style_content(self):
        styleContentList = self.get_style_content_in_dom_node
        styleContentList.extend(self.get_style_content_in_css)
        styleContentList = map(lambda style: style.strip(), styleContentList)
        return styleContentList

    '''
    描述： 获取包含script的所有<script>标签下为js样式的链接
    '''

    @property
    def get_script_tag_js_list(self):
        scriptTagJsList = []
        for link in self.get_links_from_doc:
            if link[0].tag == 'script' and 'src' in link[0].keys():
                src = link[0].get("src")
                if src.endswith('.js'):
                    scriptTagJsList.append(src)
        return scriptTagJsList

    '''
    描述： 获取当面dom分支下的所有script內容
    '''

    @property
    def get_script_content_in_dom_node(self):
        scriptContentList = []
        if self.doc is not None:
            try:
                scriptNodeList = self.doc.xpath("//script")
                scriptContentList.extend([node.text_content() for node in scriptNodeList])
            except Exception, e:
                raise DarkException, _('Failed to get script by doc.xpath. Exception: %(exception)s.' % {'exception': str(e)})
        return scriptContentList

    '''
    描述： 从js文件中获取script内容
    '''

    @property
    def get_script_content_in_js(self):
        scriptContentList = []
        for js in self.get_script_tag_js_list:
            request = Requset(js, 1)
            request.run()
            req = request.get_text()
            if req is not None:
                scriptContentList.append(req)
        return scriptContentList

    '''
    描述： 获取当前html中的全部style内容
    '''

    def get_all_script_content(self):
        scriptContentList = self.get_script_content_in_dom_node
        scriptContentList.extend(self.get_script_content_in_js)
        scriptContentList = map(lambda script: script.strip(), scriptContentList)
        return scriptContentList

    '''
    描述： 获取当前页面中某个元素的所有兄弟元素， 如过includeSelf标志为Ture，则表示包含当前元素
    '''

    def get_all_brother_element(self, element, includeSelf=True):
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

    '''
    描述： 获取当前页面中某个元素的所有祖先元素
    '''

    def get_all_parent_element(self, element):
        parentList = []
        while element is not None:
            parent = element.getparent()
            if (parent is not None) and parent.tag != 'html':
                # print 'get_all_parent_element :' + parent.tag
                parentList.append(parent)
            element = parent
        return parentList

    '''
    描述： 获取当前页面中某个元素的所有后代元素
    '''

    def get_all_child_element(self, element):
        return element.getchildren()

    '''
    描述： 打印当前页面中某个元素的信息
    '''

    def print_element(self, element):
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

    '''
    描述： 提取某个元素中某个样式的值
    '''

    def get_element_style_attr_value(self, element, attrString):
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
                #print match.group(1)
                return match.group(1)
            else:
                return
        else:
            return

    '''
    描述： 获取html中的javascript方法中的ID
    '''
    def get_id_in_javascript(self, functionName):
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
            except Exception, e:
                print 'htmlParser.html_obj.get_id_in_javascript: %s' % e
        return matchList

    '''
    描述： 获取html中的class对应的style
    '''
    def get_style_in_class(self, className):
        for script in self.styles:
            try:
                match = re.search(r'%s\x20[^\{]*\{([^\}]+)\}' % className, script, re.IGNORECASE | re.DOTALL)
                if match is not None:
                    return match.group(1)
            except Exception, e:
                print 'htmlParser.html_obj.get_style_in_class: %s' % e
        return None


if __name__ == '__main__':
    url = "http://sa.offcn.com/"
    htObj = html_object(url)
    print htObj.javaScripts
    # htObj.set_paresr_doc()

    #aList = htObj.get_a_tag_link_list()

    '''
    styleList = htObj.get_all_style_content()  # 获取所有的非style属性下的样式
    for style in styleList:
        print style

    print '____________________________'

    scriptList = htObj.get_all_script_content()  # 获取当前页面中的所有javascript
    for script in scriptList:
        print script
    '''
