#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
描述： 该模块提供访问数据库的API接口，支持的数据库有MySQL、SQLite、PostGreSQL。
'''
import threading
from core.exception.DarkException import DarkException


class DBClient(object):
    '''
    描述： 定义dark数据库访问接口基类。
    '''

    def __init__(self):
        self._db = None                     # 数据库对象
        self._insertionCount = 0            # 等待执行commit的数目
        self._commitNumber = 50
        self._dbLock = threading.RLock()    # 线程锁

    def connect(self):
        '''
        描述： 打开一个数据库连接，子类实现。
        '''
        raise NotImplementedError

    def _commit(self, urg=False):
        '''
        描述： 每调用N次这个方法，才执行一次真正意义的commit，N默认值是50。
        @:parameter urg: 标志是否紧急commit。
        '''
        if urg:
            try:
                self._db.commit()
            except Exception, e:
                raise DarkException('The database layer of object ' \
                                           'persistence raised and exception while [commit]: ' + str(e))
            else:
                self._insertionCount = 0  # 无异常，执行此处， 将待执行数目+1
        else:
            self._insertionCount += 1
            if self._insertionCount > self._commitNumber:
                try:
                    self._db.commit()
                except Exception, e:
                    raise DarkException('The database layer of object ' \
                                               'persistence raised and exception while [commit]: ' + str(e))
                else:
                    self._insertionCount = 0

    def retrieveRows(self, sql, parameters=(), all=False):  # @ReservedAssignment
        '''
        描述： 执行SQL语句提取数据行，主要是执行DQL（Data Query Language）语句。
        @:parameter sql: 参数化的SQL语句。
        @:parameter parameters: 参数值列表或元组。
        @return: 返回查询结果，值是列表或元组(取决数据库类型)。
        '''
        rows = []
        c = self.cursor()
        with self._dbLock:
            try:
                c.execute(sql, parameters)
                rows = c.fetchall() if all else c.fetchone()
            except Exception, e:
                raise DarkException('The database layer of object ' \
                                           'persistence raised and exception while [retrieveRows]: ' + str(e))
        return rows

    def executeSql(self, sql, parameters=(), commit_urg=False):
        '''
        描述： 执行SQL语句，主要是执行DDL（Data Definition Language）、DCL（Data Control Language）、DML（Data Manipulation Language）语句。
        @:parameter sql: 参数化的SQL语句。
        @:parameter parameters：参数值列表或元组。
        '''
        c = self.cursor()
        with self._dbLock:
            try:
                c.execute(sql, parameters)
                self._commit(urg=commit_urg)
            except Exception, e:
                raise DarkException('The database layer of object ' \
                                           'persistence raised and exception while [executeSql]: ' + str(e))

    def callProcedure(self, name, parameters=()):
        '''
        描述:执行存储过程。
        @:parameter name：存储过程名称。
        @:parameter parameters：参数值列表或元组。
        '''
        c = self._db.cursor()
        with self._dbLock:
            try:
                c.callproc(name, parameters)
                self._commit()
            except Exception:
                raise

    def createTable(self, name, columns=(), primaryKeyColumns=[]):
        '''
        描述： 创建数据表(提供一种便捷的创建数据表的方式)。
        @:parameter name：数据表名。
        @:parameter columns：列表或元组，包含二元组，每个二元组指定一个待建数据列的名称和类型。
        @:parameter primaryKeyColumns：列表或元组，包含数据表主键列名称字符串。
        '''
        raise NotImplementedError

    def dropTable(self, name):
        '''
        描述： 删除数据表
        @:parameter name：数据表名。
        '''
        raise NotImplementedError

    def createIndex(self, table, columns):
        '''
        描述： 创建索引(提供一种便捷的创建数据表索引的方式)。
        @parameter table: 待建索引数据表名称。
        @parameter columns: 列表或元组，包含数据列名称字符串。
        '''
        raise NotImplementedError

    def dropIndex(self, table):
        '''
        描述： 删除数据表
        @:parameter table：数据表名。
        '''
        raise NotImplementedError

    def cursor(self):
        '''
        描述： 返回一个新的索引对象。
        '''
        return self._db.cursor()

    def close(self):
        '''
        描述： commit并关闭连接。
        '''
        self._db.commit()
        self._db.close()
