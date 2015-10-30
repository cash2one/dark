#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 黑名单信息
BL_DATA_TABLE = 'blacklist'

BL_COLUMNS = [
    ('blId', 'INT AUTO_INCREMENT'),
    ('keyword', 'VARCHAR(5) NOT NULL')
]

BL_PRIMARY_KEY_COLUMNS = ('blId',)

BL_INDEX_COLUMNS = ('keyword',)

BL_SEARCH_WORD = 'keyword'

BL_STORE_WORD = 'keyword'


# 白名单信息
WL_DATA_TABLE = 'whitelist'

WL_COLUMNS = [
    ('wlId', 'INT AUTO_INCREMENT'),
    ('domain', 'VARCHAR(100) NOT NULL UNIQUE'),
    ('domainTitle', 'VARCHAR(80)')
]

WL_PRIMARY_KEY_COLUMNS = ('wlId',)

WL_INDEX_COLUMNS = ('domain',)

WL_SEARCH_WORD = 'domain'

WL_STORE_WORD = ('domain', 'domainTitle', )

# 检测信息
DT_DATA_TABLE = 'detectInfo'

DT_COLUMNS = [
    ('dtId', 'INT AUTO_INCREMENT'),
    ('url', 'VARCHAR(100) NOT NULL'),
    ('hiddenUrl', 'VARCHAR(500)'),
    ('hiddenLevel', 'VARCHAR(6)'),
    ('hiddenType', 'VARCHAR(25)')
]

DT_PRIMARY_KEY_COLUMNS = ('dtId',)

DT_INDEX_COLUMNS = ('hiddenUrl', 'hiddenLevel', 'hiddenType')

DT_SEARCH_WORD = ''

DT_STORE_WORD = ('url', 'hiddenUrl', 'hiddenLevel', 'hiddenType')


# profile.py中的配置
DEFAULT_ENCODING = 'utf-8'

# htmlparser.py中的配置
HTML_TIMEOUT = 20

# compare.py 中的配置
FONT_SIZE = 1
FONT_SIZE_PERCENT = 10

LINE_HEIGHT = 1
LINE_HEIGHT_PERCENT = 10

POSITION_TOP = -400
POSITION_TOP_PERCENT = -100

POSITION_LEFT = -100
POSITION_LEFT_PERCENT = -100

TEXT_INDENT = -400
TEXT_INDENT_PERCENT = -100

HEIGHT_MAX = 10
WIDTH_MAX = 10
SCROLLAMOUNT_MIN = 1000

OVER_WIDTH = 5
OVER_HEIGHT = 5

# threadManager.py
THREAD_MAX = 10
QUEUE_SIZE = 200

# textFile.py
LOG_FILE = "/tmp/dark.log"

# browser.py
BROWSER_TYPE = 'phantomjs'

# detect.py
RETRY_TIMES_MAX = 5
RANDOM_NUM = 3

# hiddenDetect.py
REPORT_PATH = '/tmp'
DEPTH_LIMIT = 2