#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from DBClient import DBClient
from wherehelper import WhereHelper
import _mysql_exceptions as DB_EXC
from core.exception.DarkException import DarkManagerException
from i18n import _

class DBClientMySql(DBClient):
    '''
    MySQL数据库操作client(helper)。
    '''

    def __init__(self, user, password, db=None, host='localhost', port='3306', charset='utf8'):
        '''
        构造函数。

        @param host: 服务期地址, 默认localhost。
        @param user: 用户名。
        @param password: 密码。
        @param db: 数据库名。
        @param port: 数据库端口，默认3306。
        @param charset: 字符集。
        '''
        self.host = host
        self.db = db
        self.user = user
        self.passwd = password
        self.port = port
        self.charset = charset
        DBClient.__init__(self)
        super(DBClientMySql, self).__init__()



    def connect(self):
        '''
        建立数据库连接。
        '''
        try:
            if self.host == 'localhost' or self.host == '127.0.0.1':
                if self.db:
                    self._db = MySQLdb.connect(host=self.host,
                                               user=self.user,
                                               passwd=self.passwd,
                                               db=self.db)
                else:
                    self._db = MySQLdb.connect(host=self.host,
                                               user=self.user,
                                               passwd=self.passwd)
            else:
                if self.db:
                    self._db = MySQLdb.connect(host=self.host,
                                               port=self.port,
                                               user=self.user,
                                               passwd=self.passwd,
                                               db=self.db)
                else:
                    self._db = MySQLdb.connect(host=self.host,
                                               user=self.user,
                                               passwd=self.passwd)

            self._db.set_character_set(self.charset)
            self._db.autocommit(True)
        except DB_EXC.Error, e:
            raise DarkManagerException('MySql Error: %d: %s' % (e.args[0], e.args[1]))

    def selectDb(self, db):
        '''
        选择数据库。
        '''
        try:
            self._db.select_db(db)
        except DB_EXC.Error, e:
            raise DarkManagerException('MySql Error: %d: %s' % (e.args[0], e.args[1]))


    def is_table_exist(self, table):
        '''
        检测数据表是否存在数据库中
        @param table:数据表名
        @return: boolean
        '''
        sql = 'SELECT table_name FROM `INFORMATION_SCHEMA`.`TABLES` WHERE table_name = \'%s\'' % table
        try:
            row = self.retrieveRows(sql, (), True)
        except Exception, e:
            raise DarkManagerException('The database layer of object'\
                                       'persistence raised and exception while [is_table_exist]: ' + str(e))
        if row:
            return True
        return False

    def is_index_exist(self, index):
        '''
        检测数据库中是否存在索引
        @param index:索引名
        @return: boolean
        '''
        sql = 'SELECT * FROM `INFORMATION_SCHEMA`.`STATISTICS` WHERE index_name = \'%s\'' % index
        try:
            row = self.retrieveRows(sql, (), True)
        except Exception, e:
            raise DarkManagerException('The database layer of object '\
                                       'persistence raised and exception while [is_table_exist]: ' + str(e))
        if row:
            return True
        return False

    def createTable(self, table, columns=(), primaryKeyColumns=[]):
        '''
        创建数据表(提供一种便捷的创建数据表的方式)。

        @param table：数据表名。
        @param columns：列表或元组，包含二元组，每个二元组指定一个待建数据列的名称和类型。
        @param primaryKeyColumns：列表或元组，包含数据表主键列名称字符串。
        '''
        if not self.is_table_exist(table):
            sql = 'CREATE TABLE ' + table + '('
            for columnData in columns:
                columnName, columnType = columnData
                sql += columnName + ' ' + columnType + ', '
            sql += 'PRIMARY KEY (' + ','.join(primaryKeyColumns) + '))'
            sql += 'DEFAULT CHARSET=UTF8'
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkManagerException('The database layer of object '\
                                           'persistence raised and exception while [createTable]: ' + str(e))
        else:
            print ('The database layer of object '\
                                       'persistence raised and exception while [createTable]: ' + 'table exist!')


    def dropTable(self, table):
        '''
         删除数据表
        @param table：数据表名。
        '''
        if self.is_table_exist(table):
            sql = 'DROP TABLE %s' % table
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkManagerException('The database layer of object'\
                                           'persistence raised and exception while [dropTable]: ' + str(e))
        else:
            print ('The database layer of object'\
                                       'persistence raised and exception while [dropTable]: ' + 'table not exist!')

    def createIndex(self, table, columns):
        '''
        创建索引(提供一种便捷的创建数据表索引的方式)。

        @parameter table: 待建索引数据表名称。
        @parameter columns: 列表或元组，包含数据列名称字符串。
        '''
        if not self.is_index_exist('%s_index' % table):
            sql = 'CREATE INDEX %s_index ON %s( %s )' % (table, table, ','.join(columns))
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkManagerException('The database layer of object '\
                                           'persistence raised and exception while [createIndex]: ' + str(e))
        else:
            print ('The database layer of object '\
                                       'persistence raised and exception while [createIndex]: ' + 'index exist!')

    def dropIndex(self, table):
        '''
         删除数据表
        @param table：数据表名。
        '''
        if self.is_index_exist('%s_index' % table):
            sql = 'DROP INDEX %s_index ON %s' % (table, table)
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkManagerException('The database layer of object '\
                                           'persistence raised and exception while [dropIndex]: ' + str(e))
        else:
            print ('The database layer of object'\
                                       'persistence raised and exception while [dropIndex]: ' + 'index not exist!')

    def find_data(self, table, searchData):
        """
        从当前的数据库中查找数据

        @:parameter search_data，数据格式如下 [(name, value, operator), ...]
        @:parameter table 要查找的表名
        return True or False
        """
        if searchData:
            sql = 'SELECT * FROM ' + table
            where = WhereHelper(searchData)
            sql += where.sql()
            try:
                row = self.retrieveRows(sql, where.values())
                if row:
                    return True
            except Exception, e:
                print e
                msg = 'You performed an invalid search. Please verify your syntax.'
                raise Exception(msg)
            return False
        return False

    def get_data(self, table, searchData, result_limit=-1, orderData=[]):
        """
        从数据库中获取数据
        @:parameter table，要查找的表名
        @:parameter search_data， 要查找的数据组数据格式如下 [(name, value, operator), ...]
        @:parameter orderData = [(name, direction)]
        @:parameter result_limit， 要查找的条数，默认为-1（不开启）
        return list
        """
        result = []
        if searchData:
            sql = 'SELECT * FROM ' + table
            where = WhereHelper(searchData)
            sql += where.sql()
            orderby = ""
            #
            # TODO we need to move SQL code to parent class
            #
            for item in orderData:
                orderby += item[0] + " " + item[1] + ","
            orderby = orderby[:-1]

            if orderby:
                sql += " ORDER BY " + orderby

            if result_limit is not -1:
                sql += ' LIMIT ' + str(result_limit)
            else:
                pass
            try:
                rows = self.retrieveRows(sql, where.values())
                if rows:
                    for row in rows:
                        result.append(row)
            except Exception, e:
                msg = 'You performed an invalid search. Please verify your syntax.'
                raise Exception(msg)
        return result

    def delete_data(self, table, deleteData):
        """
        从数据库中删除数据
        @:parameter table，要查找的表名
        @:parameter deleteData，要删除的条件，数据格式如下(name, value, operator)
        """
        if deleteData:
            sql = 'DELETE FROM ' + table
            where = WhereHelper(deleteData)
            sql += where.sql()
            try:
                self.executeSql(sql, where.values())
            except Exception:
                msg = 'You performed an invalid search. Please verify your syntax.'
                raise Exception(msg)

    def insert_data(self, table, insertData ,update=False):
        """
        从数据库中插入数据
        @:parameter table，要查找的表名
        @:parameter insertData，要插入的条件，数据格式如下[(name, value)]
        @:parameter update，是否要更新数据
        """
        if insertData:
            if update:
                sql = 'REPLACE INTO ' + table
            else:
                sql = 'INSERT INTO ' + table
            cols = ""
            values = ""
            valueList = []
            for item in insertData:
                cols += item[0] + ","
                values += "%s" + ","
                valueList.append(item[1])
            cols = cols[:-1]
            values = values[:-1]
            sql += '(' + cols +') VALUES(' + values + ')'

            try:
                self.executeSql(sql, valueList)
            except Exception, e:
                print e
                msg = 'You performed an invalid insert. Please verify your syntax.'
                raise Exception(msg)

    def disconnect(self):
        """
        关闭数据库连接
        """
        self.close()