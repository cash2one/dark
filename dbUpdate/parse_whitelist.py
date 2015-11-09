#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'jason'

import sys,os
import MySQLdb
from dark_core.request import Requset
from parse_web import rebot_obj


reload(sys)
sys.setdefaultencoding('utf-8')

clear_sql = "truncate table whitelist;"

in_sql = "insert into whitelist(domain, domainTitle) values ('%s', '%s')"

#数据库方法
class Db_Connect:
    def __init__(self, db_host, user, pwd, db_name, charset="utf8",  use_unicode = True):
        print "init begin"
        print db_host, user, pwd, db_name, charset , use_unicode
        self.conn = MySQLdb.Connection(db_host, user, pwd, db_name, charset=charset , use_unicode=use_unicode)
        print "init end"


    def clear(self, sql):
        try:
            n = self.conn.cursor().execute(sql)
            self.conn.commit()
            return n
        except Exception, e:
            print "Error: execute sql '",sql,"' failed: %s" %e

    def insert(self, sql):
        try:
            n = self.conn.cursor().execute(sql)
            return n
        except Exception, e:
            print "Error: execute sql '",sql,"' failed: %s" %e

    def close(self):
        self.conn.commit()
        self.conn.close()

def get_html_title_by_doc(doc):
    if doc is not None:
        try:
            title = doc.xpath("/html/head/title/text()")
            if len(title):
                return title[0]
        except Exception, e:
            print 'get_html_title_by_doc: %s' % e
    return ''


def run():
    db = Db_Connect("127.0.0.1", "root", "ly6521313", "url_detect")
    db.clear(clear_sql)
    rebot = rebot_obj()
    rebot.run()
    resultList = rebot.urlList
    for result in resultList:
        db.insert(in_sql % result)
    db.close()




if __name__ == "__main__":
   run()