#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'jason'

import sys,os
import MySQLdb
from core.parser.contentParser import content_obj

reload(sys)
sys.setdefaultencoding('utf-8')

in_sql = "insert into blacklist(keyword) select \'%s\' from DUAL where not exists (select keyword from blacklist where keyword = \'%s\')"

fields = ("blId","keyword")

#数据库方法
class Db_Connect:
    def __init__(self, db_host, user, pwd, db_name, charset="utf8",  use_unicode = True):
        print "init begin"
        print db_host, user, pwd, db_name, charset , use_unicode
        self.conn = MySQLdb.Connection(db_host, user, pwd, db_name, charset=charset , use_unicode=use_unicode)
        print "init end"

    def insert(self, sql):
        try:
            n = self.conn.cursor().execute(sql)
            return n
        except Exception, e:
            print "Error: execute sql '",sql,"' failed: %s" %e

    def close(self):
        self.conn.commit()
        self.conn.close()

def run():
    keyList = []
    db = Db_Connect("127.0.0.1", "root", "ly6521313", "url_detect")
    file = open('./keyword.list', 'r')
    for line in file.readlines():
        getLine = line.strip('\n')
        if getLine.startswith(';') or getLine.startswith('#'):
            continue
        else:
            content = content_obj()
            keys = content.get_key_words_by_all(getLine, 20)
            for key in keys:
                if not key.isdigit():
                    keyList.append(key)

    for key in set(keyList):
        sql = in_sql % (key, key)
        print db.insert(sql)
    file.close()
    db.close()




if __name__ == "__main__":
   run()