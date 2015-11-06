# -*- coding: utf-8 -*-
"""
数据库管理类
"""
import MySQLdb
from hamster.configuration import Singleton
from DBUtils.PooledDB import PooledDB
# 自定义的配置文件，主要包含DB的一些基本配置


# 数据库实例化类
class DbManager(Singleton):
    def __init__(self):

        self._pool = PooledDB(creator=MySQLdb, mincached=1 , maxcached=20 ,
                              host='localhost' , port=3306 , user='root' , passwd='ly6521313' ,
                              db='url_detect',use_unicode=False,charset='utf8')

    def getConn(self):
        return self._pool.connection()


_dbManager = DbManager()


def getConn():
    """ 获取数据库连接 """
    return _dbManager.getConn()


def executeAndGetId(sql, param=None):
    """ 执行插入语句并获取自增id """
    conn = getConn()
    cursor = conn.cursor()
    if param == None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, param)
    id = cursor.lastrowid
    cursor.close()
    conn.close()

    return id


def execute(sql, param=None):
    """ 执行sql语句 """
    conn = getConn()
    cursor = conn.cursor()
    if param == None:
        rowcount = cursor.execute(sql)
    else:
        rowcount = cursor.execute(sql, param)
    cursor.close()
    conn.close()

    return rowcount


def queryOne(sql):
    """ 获取一条信息 """
    conn = getConn()
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    rowcount = cursor.execute(sql)
    if rowcount > 0:
        res = cursor.fetchone()
    else:
        res = None
    cursor.close()
    conn.close()

    return res


def queryAll(sql):
    """ 获取所有信息 """
    conn = getConn()
    cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    rowcount = cursor.execute(sql)
    if rowcount > 0:
        res = cursor.fetchall()
    else:
        res = None
    cursor.close()
    conn.close()

    return res


if __name__ == "__main__":
    res = execute('select * from whitelist limit 100')
    print str(res)

    res = queryOne('select * from whitelist limit 100')
    print str(res)

    res = queryAll('select * from whitelist limit 100')
    print str(res)
