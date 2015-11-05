#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'root'

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import os
import codecs
import sys
from core.output.logging import logger
from core.settings.settings import settings
from core.exception.DarkException import DarkException
from core.parser.urlParser import url_object
from datetime import datetime
from i18n import _


class HtmlFile(object):
    def __init__(self, obj):
        self.obj = obj  # 加载要进行报告生成的组件名
        self.target = url_object(self.obj.url).getDomain
        root_path = os.path.dirname(os.path.realpath(__file__))  # 获取当前文件的工作目录
        self.reportPath = settings.get('REPORT_PATH')  # 设置报告生成的根目录

        self._initialized = False  # 初始化标志

        self._html_filepath = root_path + os.path.sep
        self._style_main_filename = self._html_filepath + 'main.css'  # 加载的css文件位置
        # These attributes hold the file pointers
        self._file = None

        datetimestrf = datetime.now().strftime('%Y-%m-%d')

        self._file_name = self.target + '_' + datetimestrf + '_a.html'
        self._file_path = os.path.join(self.reportPath, self._file_name)

    def _init(self):
        '''
        Write messages to HTML file.
        '''
        self._initialized = True
        try:
            self._file = codecs.open(self._file_path, "w", "utf-8", 'replace')
        except IOError, io:
            msg = 'Can\'t open report file "' + os.path.abspath(self._file_path) + '" for writing'
            msg += ': "%s".' % io
            raise DarkException(msg)
        except Exception, e:
            msg = 'Can\'t open report file ' + self._file_path + ' for output.'
            msg += ' Exception: "' + str(e) + '".'
            raise DarkException(msg)

        try:
            main_style_file = open(self._style_main_filename, "r")
        except:
            raise DarkException, _('Cant open style file ' + self._html_filepath + '.')
        else:
            doctype_str = u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"' \
                          u'"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n' \
                          u'<html xmlns="http://www.w3.org/1999/xhtml">\n'
            self._write_to_file(doctype_str)
            head_str = u'<head>\n' \
                       u'\t<title>%s</title>\n' \
                       u'\t<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n' \
                       u'\t<STYLE TYPE="text/css">\n' % unicode(settings.get('HTML_TITLE'))
            self._write_to_file(head_str)
            self._write_to_file(main_style_file.read())
            headend_str = u'\n\t</style>\n</head>\n'
            self._write_to_file(headend_str)
            main_style_file.close()
            body_str = u'<body>\n'
            self._write_to_file(body_str)

    def _write_to_file(self, msg):
        '''
        Write msg to the file.

        @parameter msg: The message string.
        '''
        try:
            self._file.write(msg)
        except Exception, e:
            msg = 'An exception was raised while trying to write to the output file:', e
            logger.debug(msg)
            sys.exit(1)

    def genHtmlReport(self):
        '''
        This method is called when the scan has finished.
        '''
        # Just in case...
        if not self._initialized:
            self._init()
            try:
                malwebRes = self.obj.resultHiddenlink

                starttime = self.obj.strStartTime
                interval = self.obj.interval

                rname = u'恶意内容扫描报告'

                div_wrapper_str = u'<div id="wrapper">\n' \
                                  u'\t<div class="tt">\n' \
                                  u'\t\t<p>深信服安全中心云扫描服务</p></div>\n'
                self._write_to_file(div_wrapper_str)

                div_header_str = u'\t<div id="header">\n' \
                                 u'\t\t<h1>WEB应用%s</h1>\n' \
                                 u'\t\t<ul>\n' \
                                 u'\t\t\t<li>目标网站：%s</li>\n' \
                                 u'\t\t\t<li>开始时间：%s</li>\n' \
                                 u'\t\t\t<li>扫描时长：%s</li>\n' \
                                 u'\t\t</ul>\n' % (rname, self.target, starttime, interval)
                self._write_to_file(div_header_str)

                if len(malwebRes) != 0:
                    malwebContRes = True
                else:
                    malwebContRes = False

                if malwebContRes == True:
                    div_tc_str = u'\t\t<div class="tc">\n' \
                                 u'\t\t\t<h2>经检测：</h2>\n' \
                                 u'\t\t\t<p>发现该网站存在恶意网页（暗链|挂马|webshell），证明该网站已经遭到入侵。请尽快删除恶意网页或内容。</p>\n' \
                                 u'\t\t</div>\n'
                    self._write_to_file(div_tc_str)
                else:
                    div_tc_str = u'\t\t<div class="tc">\n' \
                                 u'\t\t\t<h2>经检测：</h2>\n' \
                                 u'\t\t\t<p>没有发现该网站存在恶意内容。</p>\n' \
                                 u'\t\t</div>\n'
                    self._write_to_file(div_tc_str)

                div_end_str = u'\t</div>\n'
                self._write_to_file(div_end_str)

                # 目标站点信息
                div_body_str = u'\t<div class="body">\n' \
                               u'\t\t<!-- 重复性模块：开始 -->\n' \
                               u'\t\t<div class="m">\n' \
                               u'\t\t\t<div class="m-h">\n' \
                               u'\t\t\t\t<h2>恶意网页检测结果</h2>\n' \
                               u'\t\t\t</div>\n' \
                               u'\t\t\t<div class="m-b">\n'
                self._write_to_file(div_body_str)

                if len(malwebRes):
                    hdurl_num = len(malwebRes)  # 当前检测到的暗链数量
                    div_c_str = u'\t\t\t\t<div class="c">\n' \
                                u'\t\t\t\t\t<dl class="c-t">\n' \
                                u'\t\t\t\t\t\t<dt><strong>暗链（%d）</strong></dt>\n' \
                                u'\t\t\t\t\t\t<dd> <strong>描述：</strong><br/>\n' \
                                u'\t\t\t\t\t\t\t暗链是指攻击者通过各种攻击手段向网站的正常网页中植入视觉上令人难以察觉的链接，这些链接往往是网游私服、医疗、博彩、色情，甚至是反动网站的网站链接。<br/>\n' \
                                u'\t\t\t\t\t\t\t<strong>修复建议：</strong><br/>\n' \
                                u'\t\t\t\t\t\t\t删除暗链代码，同时修复网站漏洞防止再次被植入暗链。\n' \
                                u'\t\t\t\t\t\t</dd>\n' \
                                u'\t\t\t\t\t</dl>\n' \
                                u'\t\t\t\t\t<div class="c-l">\n' % hdurl_num
                    self._write_to_file(div_c_str)

                    k = 0
                    # hd_url: 包含暗链的分支网站， hd_set： 该分支网站下的暗链信息{url:(content, level, type)}
                    for (hd_url, hd_set) in malwebRes.items():
                        k = k + 1
                        links_html = u''
                        for (include_url, include_property) in hd_set.items():
                            content = include_property[0]
                            level = include_property[1]
                            type = include_property[2]
                            links_html += u'\t\t\t\t\t\t\t\t\t<li>链接：%s\t内容：%s\t等级：%s\t类型：%s</li>\n' % (include_url, content, level, type)

                        div_c_item_str = u'\t\t\t\t\t\t<div class="c-item">\n' \
                                         u'\t\t\t\t\t\t\t<div class="c-h">\n' \
                                         u'\t\t\t\t\t\t\t\t<h3>恶意网页%d/%d</h3>\n' \
                                         u'\t\t\t\t\t\t\t</div>\n' \
                                         u'\t\t\t\t\t\t\t<div class="c-b">\n' \
                                         u'\t\t\t\t\t\t\t\t<dl>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dt>页面URL:</dt>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dd><a href="%s">发现"%s"存在暗链</a></dd>\n' \
                                         u'\t\t\t\t\t\t\t\t</dl>\n' \
                                         u'\t\t\t\t\t\t\t\t<dl>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dt>严重等级：</dt>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dd><strong class="high">%s</strong>\n' \
                                         u'\t\t\t\t\t\t\t\t</dl>\n' \
                                         u'\t\t\t\t\t\t\t\t<dl>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dt>恶意内容：</dt>\n' \
                                         u'\t\t\t\t\t\t\t\t\t<dd></dd>\n' \
                                         u'\t\t\t\t\t\t\t\t</dl>\n' \
                                         u'\t\t\t\t\t\t\t\t<code class="quote">\n' \
                                         u'%s' \
                                         u'\t\t\t\t\t\t\t\t</code>\n' \
                                         u'\t\t\t\t\t\t\t</div>\n' \
                                         u'\t\t\t\t\t\t</div>\n' % (k, hdurl_num, hd_url, hd_url, settings.get('THREAT_LEVEL'), links_html)
                        self._write_to_file(div_c_item_str)
                    div_end_str = u'\t\t\t\t\t</div>\n' \
                                  u'\t\t\t\t</div>\n' \
                                  u'\t\t\t</div>\n'

                    self._write_to_file(div_end_str)

                else:
                    div_c_str = u'\t\t\t\t未发现任何恶意网页！\n'
                    self._write_to_file(div_c_str)
                    div_end_str = u'\t\t\t</div>\n'
                    self._write_to_file(div_end_str)

                div_end_str = u'\t\t</div>\n' \
                              u'\t</div>\n'
                self._write_to_file(div_end_str)

                html_end_str = u'</div>\n</body>\n</html>\n'
                self._write_to_file(html_end_str)

            except Exception, e:
                logger.error('Why this happen, report will return none:%s' % e)
                self._file.close()
                return None
        else:
            self._file.close()

        datetimestrf = datetime.now().strftime('%Y-%m-%d')
        import shutil

        typestr = '恶意内容扫描报告'

        dir = self.target
        fin_dir = os.path.join(self.reportPath, dir)
        fin_path = os.path.join(fin_dir, datetimestrf + '_' + typestr + '.html')

        if not os.path.exists(fin_dir):
            os.mkdir(fin_dir)

        shutil.move(self._file_path, fin_path)

        return fin_path
