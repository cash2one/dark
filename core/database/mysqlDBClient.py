#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from DBClient import DBClient
from wherehelper import WhereHelper
import _mysql_exceptions as DB_EXC
from core.exception.DarkException import DarkException
from i18n import _


class DBClientMySql(DBClient):
    '''
    描述： MySQL数据库操作client(helper)。
    '''

    def __init__(self, user, password, db=None, host='localhost', port='3306', charset='utf8'):
        '''
        描述： 构造函数。
        @:parameter host: 服务期地址, 默认localhost。
        @:parameter user: 用户名。
        @:parameter password: 密码。
        @:parameter db: 数据库名。
        @:parameter port: 数据库端口，默认3306。
        @:parameter charset: 字符集。
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
        描述： 建立数据库连接。
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
            raise DarkException, _('MySql Error: %d: %s' % (e.args[0], e.args[1]))

    def selectDb(self, db):
        '''
        描述: 选择数据库。
        '''
        try:
            self._db.select_db(db)
        except DB_EXC.Error, e:
            raise DarkException, _('MySql Error: %d: %s' % (e.args[0], e.args[1]))

    def is_table_exist(self, table):
        '''
        描述： 检测数据表是否存在数据库中
        @:parameter table:数据表名
        @return: boolean
        '''
        sql = 'select table_name from `INFORMATION_SCHEMA`.`TABLES` where table_name = \'%s\'' % table
        try:
            row = self.retrieveRows(sql, (), True)
        except Exception, e:
            raise DarkException, _('The database layer of object' \
                                          'persistence raised and exception while [is_table_exist]: ' + str(e))
        if row:
            return True
        return False

    def is_index_exist(self, index):
        '''
        检测数据库中是否存在索引
        @:parameter index:索引名
        @return: boolean
        '''
        sql = 'select * FROM `INFORMATION_SCHEMA`.`STATISTICS` where index_name = \'%s\'' % index
        try:
            row = self.retrieveRows(sql, (), True)
        except Exception, e:
            raise DarkException, _('The database layer of object ' \
                                          'persistence raised and exception while [is_table_exist]: ' + str(e))
        if row:
            return True
        return False

    def createTable(self, table, columns=(), primaryKeyColumns=[]):
        '''
        创建数据表(提供一种便捷的创建数据表的方式)。

        @:parameter table：数据表名。
        @:parameter columns：列表或元组，包含二元组，每个二元组指定一个待建数据列的名称和类型。
        @:parameter primaryKeyColumns：列表或元组，包含数据表主键列名称字符串。
        '''
        if not self.is_table_exist(table):
            sql = 'create table ' + table + '('
            for columnData in columns:
                columnName, columnType = columnData
                sql += columnName + ' ' + columnType + ', '
            sql += 'primary key (' + ','.join(primaryKeyColumns) + '))'
            sql += 'default charset=utf8'
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkException, _('The database layer of object ' \
                                              'persistence raised and exception while [createTable]: ' + str(e))
        else:
            msg = 'Table which want to create is existed!'
            raise DarkException, _('The database layer of object ' \
                                          'persistence raised and exception while [createTable]: ' + str(msg))

    def dropTable(self, table):
        '''
        描述： 删除数据表
        @:parameter table：数据表名。
        '''
        if self.is_table_exist(table):
            sql = 'drop table %s' % table
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkException, _('The database layer of object' \
                                              'persistence raised and exception while [dropTable]: ' + str(e))
        else:
            msg = 'Table which want to drop not exist!'
            raise DarkException, _('The database layer of object' \
                                          'persistence raised and exception while [dropTable]: ' + str(msg))

    def createIndex(self, table, columns):
        '''
        描述： 创建索引(提供一种便捷的创建数据表索引的方式)。

        @:parametereter table: 待建索引数据表名称。
        @:parametereter columns: 列表或元组，包含数据列名称字符串。
        '''
        if not self.is_index_exist('%s_index' % table):
            sql = 'create INDEX %s_index on %s( %s )' % (table, table, ','.join(columns))
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkException, _('The database layer of object ' \
                                              'persistence raised and exception while [createIndex]: ' + str(e))
        else:
            msg = 'Index which want to create is existed!'
            raise DarkException, _('The database layer of object ' \
                                          'persistence raised and exception while [createIndex]: ' + str(msg))

    def dropIndex(self, table):
        '''
        描述： 删除数据表
        @:parameter table：数据表名。
        '''
        if self.is_index_exist('%s_index' % table):
            sql = 'drop index %s_index on %s' % (table, table)
            try:
                self.executeSql(sql, None, True)
            except Exception, e:
                raise DarkException, _('The database layer of object ' \
                                              'persistence raised and exception while [dropIndex]: ' + str(e))
        else:
            msg = 'Index which want to drop is not exist!'
            raise DarkException, _('The database layer of object' \
                                          'persistence raised and exception while [dropIndex]: ' + str(msg))

    def find_data(self, table, searchData):
        """
        描述： 从当前的数据库中查找数据
        @:parameter search_data，数据格式如下 [(name, value, operator), ...]
        @:parameter table 要查找的表名
        return True or False
        """
        if searchData:
            sql = 'select * from ' + table
            where = WhereHelper(searchData)
            sql += where.sql()
            try:
                row = self.retrieveRows(sql, where.values())
                if row:
                    return True
            except Exception, e:
                raise DarkException, _('The database layer of object' \
                                              'persistence raised and exception while [find_data]: ' + str(e))
            return False
        return False

    def get_data(self, table, searchData, result_limit=-1, orderData=[]):
        """
        描述： 从数据库中获取数据
        @:parameter table，要查找的表名
        @:parameter search_data， 要查找的数据组数据格式如下 [(name, value, operator), ...]
        @:parameter orderData = [(name, direction)]
        @:parameter result_limit， 要查找的条数，默认为-1（不开启）
        return list
        """
        result = []
        if searchData:
            sql = 'select * from ' + table
            where = WhereHelper(searchData)
            sql += where.sql()
            orderby = ""
            for item in orderData:
                orderby += item[0] + " " + item[1] + ","
            orderby = orderby[:-1]

            if orderby:
                sql += " order by " + orderby

            if result_limit is not -1:
                sql += ' limit ' + str(result_limit)
            else:
                pass
            try:
                rows = self.retrieveRows(sql, where.values())
                if rows:
                    for row in rows:
                        result.append(row)
            except Exception, e:
                raise DarkException, _('The database layer of object' \
                                              'persistence raised and exception while [get_data]: ' + str(e))
        return result

    def delete_data(self, table, deleteData):
        """
        描述： 从数据库中删除数据
        @:parameter table，要查找的表名
        @:parameter deleteData，要删除的条件，数据格式如下(name, value, operator)
        """
        if deleteData:
            sql = 'delete from ' + table
            where = WhereHelper(deleteData)
            sql += where.sql()
            try:
                self.executeSql(sql, where.values())
            except Exception, e:
                raise DarkException, _('The database layer of object' \
                                              'persistence raised and exception while [delete_data]: ' + str(e))

    def insert_data(self, table, insertData, update=False):
        """
        描述： 从数据库中插入数据
        @:parameter table，要查找的表名
        @:parameter insertData，要插入的条件，数据格式如下[(name, value)]
        @:parameter update，是否要更新数据
        """
        if insertData:
            if update:
                sql = 'replace into ' + table
            else:
                sql = 'insert into ' + table
            cols = ""
            values = ""
            valueList = []
            for item in insertData:
                cols += item[0] + ","
                values += "%s" + ","
                valueList.append(item[1])
            cols = cols[:-1]
            values = values[:-1]
            sql += '(' + cols + ') values(' + values + ')'

            try:
                self.executeSql(sql, valueList)
            except Exception, e:
                DarkException, _('The database layer of object' \
                                        'persistence raised and exception while [insert_data]: ' + str(e))

    def disconnect(self):
        """
        描述： 关闭数据库连接
        """
        self.close()
