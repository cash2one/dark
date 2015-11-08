#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from core.database.mysqlManger import sqlMg
from core.exception.DarkException import DarkException
from i18n import _


def find_keyword_from_blacklist(string):
    if string:
        sql = 'select * from blacklist where keyword = %s'
        param = (string)
        result = sqlMg.get_all(sql, param)
        if result:
            return True
        else:
            return False
    else:
        raise DarkException, _('Error string give from find keyword from blacklist function! Please check it!')
    return False


def find_domain_from_whitelist(string):
    if string:
        sql = 'select * from whitelist where domain = %s'
        param = (string)
        result = sqlMg.get_all(sql, param)
        if result:
            return True
        else:
            return False
    else:
        raise DarkException, _('Error string give from find domain from whitelist function! Please check it!')
    return False


def store_url_hidden_type_to_detect_info(url, hidden, level, type):
    if url:
        sql = 'insert into detectInfo(url, hiddenUrl, hiddenLevel, hiddenType) values(%s, %s, %s, %s)'
        param = (url, hidden, level, type)
        sqlMg.insert_one(sql, param)
        sqlMg.end()
    else:
        raise DarkException, _('Error string give from store url hidden type to detect info function! Please check it!')


def store_url_hidden_report_in_monitor_statistic(id, ref_id, threat_name, threat_level, threat_sum, stat_time,
                                                 report_part_path):
    sql = 'insert into monitor_statistic(ID, RefSiteId, ThreatName, ThreatLevel, ThreatSum, StatisticTime, ReportName) ' \
          'values(%s, %s, %s, %s, %s, %s, %s)'
    param = (id, ref_id, threat_name, threat_level, threat_sum, stat_time, report_part_path)
    sqlMg.insert_one(sql, param)
    sqlMg.end()


def get_id_from_monitor_sites_by_url(url):
    if url:
        sql = 'select id from monitor_sites where SiteUrl = %s'
        param = (url)
        result = sqlMg.get_one(sql, param)
        return result['id']
    else:
        raise DarkException, _('Error string give from get id from monitor sites by url function! Please check it!')
    return None


def create_blacklist_table():
    sql = 'create table blacklist(blId INT AUTO_INCREMENT PRIMARY KEY, keyword VARCHAR(5) NOT NULL)'
    try:
        sqlMg.create(sql)
    except Exception, e:
        raise DarkException, _('Create blacklist table failed! Please check it! Exception: %s' % e)


def create_whitelist_table():
    sql = 'create table whitelist(wlId INT AUTO_INCREMENT PRIMARY KEY, domain VARCHAR(100) NOT NULL UNIQUE, domainTitle VARCHAR(80))'
    try:
        sqlMg.create(sql)
    except Exception, e:
        raise DarkException, _('Create whitelist table failed! Please check it! Exception: %s' % e)


def create_detect_info_table():
    sql = 'create table detectInfo(dtId INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(100) NOT NULL, hiddenUrl VARCHAR(500), hiddenLevel VARCHAR(10), hiddenType VARCHAR(25) )'
    try:
        sqlMg.create(sql)
    except Exception, e:
        raise DarkException, _('Create detectInfo table failed! Please check it! Exception: %s' % e)


if __name__ == '__main__':
    #create_blacklist_table()
    # create_whitelist_table()
    create_detect_info_table()
    print get_id_from_monitor_sites_by_url('http://www.baidu.com')
    str = '博彩'
    print find_keyword_from_blacklist(str)
    str = 'www.baidu.com'
    print find_domain_from_whitelist(str)
    store_url_hidden_type_to_detect_info('a', 'a', 'a', 'a')
