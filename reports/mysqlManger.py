# -*- coding: UTF-8 -*-
"""
desc:数据库操作类
@note:
1、执行带参数的SQL时，请先用sql语句指定需要输入的条件列表，然后再用tuple/list进行条件批配
２、在格式SQL中不需要使用引号指定数据类型，系统会根据输入参数自动识别
３、在输入的值中不需要使用转意函数，系统会自动处理
"""

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from core.profile.profile import pf


class DbManager(object):
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = DbManager.getConn()
        释放连接对象;conn.close()或del conn
    """

    # 连接池对象
    __pool = None

    def __init__(self):
        """
        数据库构造函数，从连接池中取出连接，并生成操作游标
        """
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn():
        """
        描述: 静态方法，从连接池中取出连接
        @:return MySQLdb.connection
        """
        if DbManager.__pool is None:
            __pool = PooledDB(creator=MySQLdb,
                              mincached=pf.getProfileValue('db', 'mincached', 'int'),
                              maxcached=pf.getProfileValue('db', 'maxcached', 'int'),
                              cursorclass=DictCursor,
                              use_unicode=False,
                              **pf.getDbUserInfo())
        return __pool.connection()

    def get_all(self, sql, param=None):
        """
        描述: 执行查询，并取出所有结果集
        @:parameter sql:查询SQL，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @:parameter param: 可选参数，条件列表值（元组/列表）
        @:return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def get_one(self, sql, param=None):
        """
        描述: 执行查询，并取出第一条
        @:parameter sql:查询SQL，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @:parameter param: 可选参数，条件列表值（元组/列表）
        @:return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def get_many(self, sql, num, param=None):
        """
        描述: 执行查询，并取出num条结果
        @:parameter sql:查询SQL，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @:parameter num:取得的结果条数
        @:parameter param: 可选参数，条件列表值（元组/列表）
        @:return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insert_one(self, sql, value):
        """
        描述: 向数据表插入一条记录
        @:parameter sql:要插入的SQL格式
        @:parameter value:要插入的记录数据tuple/list
        @:return: insertId 受影响的行数
        """
        self._cursor.execute(sql, value)
        return self.__getInsertId()

    def insert_many(self, sql, values):
        """
        描述: 向数据表插入多条记录
        @:parameter sql:要插入的SQL格式
        @:parameter values:要插入的记录数据tuple(tuple)/list[list]
        @:return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        描述: 更新数据表记录
        @:parameter sql: SQL格式及条件，使用(%s,%s)
        @:parameter param: 要更新的  值 tuple/list
        @:return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        描述: 删除数据表记录
        @:parameter sql: SQL格式及条件，使用(%s,%s)
        @:parameter param: 要删除的条件 值 tuple/list
        @:return: count 受影响的行数
        """
        return self.__query(sql, param)

    def end(self, option='commit'):
        """
        描述: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        描述: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback');
        self._cursor.close()
        self._conn.close()


if __name__ == '__main__':
    mysql = DbManager()
    select = "select * from whitelist limit 100"
    params = ()
    result = mysql.get_one(select, params)
    print result
    mysql.dispose()
