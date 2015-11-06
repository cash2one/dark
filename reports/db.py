# -*- coding: utf-8 -*-
'''
db.py

Author: peta
Date: 20151012

db模块提供访问数据库的API接口，支持的数据库有MySQL、SQLite、PostGreSQL。
'''

from __future__ import with_statement

import sqlite3
import threading
import sys

from core.zeusException import ZeusException
from core.profile.profile import pf
from i18n import _


class DBClient(object):
    '''
    定义数据库访问接口基类。
    '''

    def __init__(self):
        self._filename = None
        self._con = None
        self._insertionCount = 0
        self._commitNumber = 50
        self._dbLock = threading.RLock()

    def connect(self):
        '''
        打开一个数据库连接，子类实现。
        '''
        raise NotImplementedError

    def getFileName(self):
        '''
        获取数据库文件名。

        @return: 文件名。
        '''
        return self._filename

    def _commit(self, urg=False):
        '''
        每调用N次这个方法，才执行一次真正意义的commit，N默认值是50。

        @param urg: 是否紧急commit标识。
        '''
        if urg:
            try:
                self._con.commit()
            except Exception, e:
                raise ZeusException, _('The database layer of object persistence raised an exception while [commit]. \
                                       Exception: %(exception)s.') % {'exception':str(e)}
            else:
                self._insertionCount = 0
        else:
            self._insertionCount += 1
            if self._insertionCount > self._commitNumber:
                try:
                    self._con.commit()
                except Exception, e:
                    raise ZeusException, _('The database layer of object persistence raised an exception while [commit]. \
                                           Exception: %(exception)s.') % {'exception':str(e)}
                else:
                    self._insertionCount = 0

    def retrieveRows(self, sql, parameters=(), iter=False):
        '''
        执行SQL语句提取数据行，主要是执行DQL语句。

        @param sql: 参数化的SQL语句。
        @param parameters: 参数值列表或元组。
        @param iter: 标识是否返回可迭代对象，默认为False。
        @return: 返回查询结果，值是列表或元组(取决于数据库类型)。
        '''
        c = self._con.cursor()
        with self._dbLock:
            try:
                c.execute(sql, parameters)
                if iter:
                    return c.__iter__()
                else:
                    return c.fetchall()
            except Exception, e:
                raise ZeusException, _('The database layer of object persistence raised an exception while [retrieveRows]. \
                                       Exception: %(exception)s.') % {'exception':str(e)}
    def executeSql(self, sql, parameters=(), urg=False):
        '''
        执行SQL语句，主要是执行DDL、DCL、DML语句。

        @param sql: 参数化的SQL语句。
        @param parameters：参数值列表或元组。
        @param urg: 是否紧急commit标识。
        '''
        c = self._con.cursor()
        with self._dbLock:
            try:
                result = c.execute(sql, parameters)
                self._commit(urg=urg)
                return result
            except Exception, e:
                raise ZeusException, _('The database layer of object persistence raised an exception while [executeSql]. \
                                       Exception: %(exception)s.') % {'exception':str(e)}

    def callProcedure(self, name, parameters=(), iter=False):
        '''
        执行存储过程。

        @param name：存储过程名称。
        @param parameters：参数值列表或元组。
        @param iter: 标识是否返回可迭代对象，默认为False。
        '''
        c = self._con.cursor()
        with self._dbLock:
            try:
                result = c.callproc(name, parameters)
                self._commit()
                if iter:
                    ret = c.__iter__()
                else:
                    ret = c.fetchall()
                if ret:
                    return ret
                else:
                    return result 
            except Exception, e:
                raise ZeusException, _('The database layer of object persistence raised an exception while [callProcedure]. \
                                       Exception: %(exception)s.' % {'exception':str(e)})

    def createTable(self, name, columns=(), primaryKeyColumns=[]):
        '''
        创建数据表(提供一种便捷的创建数据表的方式)。

        @param name：数据表名。
        @param columns：列表或元组，包含二元组，每个二元组指定一个待建数据列的名称和类型。
        @param primaryKeyColumns：列表或元组，包含数据表主键列名称字符串。
        '''
        sql = 'CREATE TABLE ' + name + '('
        for columnData in columns:
            columnName, columnType = columnData
            sql += columnName + ' ' + columnType + ', '
        sql += 'PRIMARY KEY (' + ','.join(primaryKeyColumns) + '))'
        c = self._con.cursor()
        c.execute(sql)
        self._con.commit()

    def createIndex(self, table, columns):
        '''
        创建索引(提供一种便捷的创建数据表索引的方式)。

        @parameter table: 待建索引数据表名称。
        @parameter columns: 列表或元组，包含数据列名称字符串。
        '''
        sql = 'CREATE INDEX %s_index ON %s(%s)' % (table, table, ','.join(columns))
        c = self._con.cursor()
        c.execute(sql)
        self._con.commit()

    def cursor(self):
        '''
        返回一个新的索引对象。
        '''
        return self._con.cursor()

    def close(self):
        '''
        commit并关闭连接。
        '''
        self._con.commit()
        self._con.close()
        self._filename = None


class DBClientSQLite(DBClient):
    '''
    SQLite数据库操作client(helper)。
    '''

    def connect(self, dbname):
        '''
        打开数据库文件，建立连接。

        @param dbname: 文件名，带路径（绝对路径和相对路径）。
        '''
        # 把文件名转换为UTF-8编码，这对windows系统以及一些特殊的字符是有必要的。
        unicodeFilename = dbname.decode(sys.getfilesystemencoding())
        self._filename = filenameUtf8 = unicodeFilename.encode("utf-8").replace(" ", "")
        try:
            self._con = sqlite3.connect(filenameUtf8, check_same_thread=False)
            self._con.text_factory = str
        except Exception, e:
            raise ZeusException, _('Failed to create the database in file "%(file)s". \
                                   Exception: %(exception)s.') % {'file':filenameUtf8, 'exception':str(e)}


class DBCLientPGSql(DBClient):
    '''
    PostGreSQL数据库操作client(helper)。
    '''

    def __init__(self, user, password, dbname, host = 'localhost', port = '5432'):
        '''
        构造函数。

        @param host: 服务器地址。
        @param user: 用户名。
        @param password: 密码。
        @param dbname: 数据库名。
        '''
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.port = port
        super(DBCLientPGSql, self).__init__()

    def connect(self):
        '''
        建立数据库连接。
        '''
        import psycopg2
        self._con = psycopg2.connect(host = self.host,
                port = self.port,
                user = self.user,
                password = self.password,
                database = self.database)


class DBCLientMySql(DBClient):
    '''
    MySQL数据库操作client(helper)。
    '''

    def __init__(self, user, password, db = None, host = '127.0.0.1', port = '3306', charset = 'utf8'):
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
        self.port = int(port)
        self.charset = charset
        super(DBCLientMySql, self).__init__()

    def connect(self):
        '''
        建立数据库连接。
        '''
        try:
            import MySQLdb
            import _mysql_exceptions as DB_EXC
        except Exception, e:
            raise ZeusException, _('Failed to import MySQLdb module. Exception: %(exception)s.') % {'exception':str(e)}
        else:
            try:
                if self.host == 'localhost' or self.host == '127.0.0.1':
                    if self.db:
                        self._con = MySQLdb.connect(host = self.host,
                                user = self.user,
                                passwd = self.passwd,
                                db = self.db)
                    else:
                        self._con = MySQLdb.connect(host = self.host,
                                user = self.user,
                                passwd = self.passwd)
                else:
                    if self.db:
                        self._con = MySQLdb.connect(host = self.host,
                                port = self.port,
                                user = self.user,
                                passwd = self.passwd,
                                db = self.db)
                    else:
                        self._con = MySQLdb.connect(host = self.host,
                                user = self.user,
                                passwd = self.passwd)

                self._con.set_character_set(self.charset)
                self._con.autocommit(True)
            except DB_EXC.Error, e:
                raise ZeusException, _('MySql Error: %(args0)d: %(args1)s.') % {'args0':e.args[0], 'args1':e.args[1]}

    def selectDb(self, db):
        '''
        选择数据库。
        '''
        try:
            import MySQLdb
            import _mysql_exceptions as DB_EXC
        except Exception, e:
            raise ZeusException, _('Failed to import MySQLdb module. Exception: %(exception)s.') % {'exception':str(e)}
        else:
            try:
                self._con.select_db(db)
            except DB_EXC.Error, e:
                raise ZeusException, _('MySql Error: %(args0)d: %(args1)s.') % {'args0':e.args[0], 'args1':e.args[1]}


class WhereHelper(object):
    '''
    简单的WHERE条件制造器。
    '''

    def __init__(self, conditions = {}):
        '''
        构造函数。

        @param conditions: 列表或元组形式的SQL语句Where条件。
        '''
        self.conditions = conditions

    def values(self):
        '''
        返回参数化SQL语句参数对应的值列表。

        @return: 值列表。
        '''
        if not self._values:
            self.sql()
        return self._values

    def _makePair(self, field, value, oper='=',  conjunction='AND'):
        '''
        辅助作用。

        @param field: 列名字段字符串。
        @param value: 字段值。
        @param oper: 操作符，默认=。
        @param conjunction: SQL连接符, and或or。

        @return: 二元组。
        '''
        result = ' ' + conjunction + ' ' + field + ' ' + oper + ' ?'
        return (result, value)

    def sql(self, whereStr=True):
        '''
        根据conditions列表或元组生成SQL子句。

        @param whereStr: 布尔值，指示是否添加Where，默认是True。
        @return: SQL子句。

        >>> w = WhereHelper( [ ('field', '3', '=') ] )
        >>> w.sql()
        ' WHERE field = ?'

        >>> w = WhereHelper( [ ('field', '3', '='), ('foo', '4', '=') ] )
        >>> w.sql()
        ' WHERE field = ? AND foo = ?'
        >>>
        '''
        result = ''
        self._values = []

        for cond in self.conditions:
            if isinstance(cond[0], list):
                item, oper = cond
                tmpWhere = ''
                for tmpField in item:
                    tmpName, tmpValue, tmpOper = tmpField
                    sql, value = self._makePair(tmpName, tmpValue, tmpOper, oper)
                    self._values.append(value)
                    tmpWhere += sql
                if tmpWhere:
                    result += " AND (" + tmpWhere[len(oper)+1:] + " )"
            else:
                sql, value = self._makePair(cond[0], cond[1], cond[2])
                self._values.append(value)
                result += sql
        result = result[5:]

        if whereStr and result:
            result = ' WHERE ' + result

        return result

    def __str__(self):
        return self.sql() + ' | ' + str(self.values())


class DbMgr(object):
    '''
    单例数据库连接池管理器。
    '''

    def __init__(self):
        _class = self.__class__
        if _class._doInit_:
            # 连接池大小。
            self._poolSize = 10
            # 信号量，用于控制对共享资源进行访问的线程数量。
            self._semaphore = threading.Semaphore(self._poolSize)
            # 列表，用于存放空闲的数据库连接。
            self._freedDbClientList = []
            # 列表，用于存放使用中的数据库连接。
            self._usedDbClientList = []
            _class._doInit_ = False

    def __new__(cls):
        '''
        这个方法真正实现了单例模式。
        '''
        _dbmgrstr = '_dbmgr_instance'
        if not cls.__dict__.get(_dbmgrstr):
            setattr(cls, _dbmgrstr, object.__new__(cls))
            cls._doInit_ = True
        return getattr(cls, _dbmgrstr)

    def setProfile(self, profile):
        '''
        设置配置文件对象。
        '''
        self.profile = profile

    def executeSql(self, sql, params=[], urg=False):
        '''
        执行SQL语句，主要是执行DDL、DCL、DML。

        @param sql: 参数化SQL语句。
        @param params: 参数值列表或元组。
        @param urg: 是否紧急commit标识。
        '''
        return self.processRequest('executeSql', sql, parameters=params, urg=urg)

    def retrieveRows(self, sql, params=[], iter=False):
        '''
        执行SQL语句提取数据行，主要是执行DQL。

        @param sql: 参数化SQL语句。
        @param params: 参数值列表或元组。
        @param iter: 标识是否返回可迭代对象，默认为False。
        @return: 返回查询结果，列表或元组（取决于数据库）。
        '''
        return self.processRequest('retrieveRows', sql, parameters=params, iter=iter)

    def callProcedure(self, name, params=[], iter=False):
        '''
        执行存储过程。

        @param name: 存储过程名称。
        @param params: 存储过程参数列表或元组。
        @param iter: 标识是否返回可迭代对象，默认为False。
        '''
        return self.processRequest('callProcedure', name, parameters=params, iter=iter)

    def processRequest(self, method, *args, **kwargs):
        '''
        提交一个到可用数据库client的请求，并调用相应client的方法。

        @param method: 数据库client方法名。
        @param *args: method的位置参数。
        @param **kwargs: method的关键字参数。
        @return: 返回数据client方法调用的结果。
        '''
        dbclient = self._getAvailableDbClient()
        if dbclient:
            try:
                return getattr(dbclient, method)(*args, **kwargs)
            finally:
                self._freeDbClient(dbclient)
        else:
            raise ZeusException, _('All %(poolSize)d database connections are busy.') % {'poolSize':self._poolsize}

    def _getAvailableDbClient(self):
        '''
        私有方法，从连接池返回一个可用的DB client，如果没有，则返回None。
        '''
        retryCount = 0
        dbclient = None

        while retryCount < 20:
            if self._semaphore.acquire():
                if self._freedDbClientList:
                    # 取第一个以循环使用。
                    dbclient = self._freedDbClientList.pop(0)
                else:
                    dbclient = self._createDbClient(pf.getDbType(), **pf.getDbInfo())
            if dbclient:
                self._usedDbClientList.append(dbclient)
                break
            else:
                retryCount += 1
                import time
                time.sleep(0.2)

        return dbclient

    def _freeDbClient(self, dbclient):
        '''
        释放DB client并存放于列表最后面，以循环使用。

        @param dbclient: DB client。
        '''
        self._freedDbClientList.append(dbclient)
        for index, dbc in enumerate(self._usedDbClientList):
            if dbclient is dbc:
                self._usedDbClientList.pop(index)
        self._semaphore.release()

    def _createDbClient(self, clienttype, **kwargs):
        '''
        返回一个DB client。

        @param clienttype: 数据库client类型，如'mysql'。
        @param **kwargs: 关键字参数，用于创建数据库client对象。
        @return: 返回一个打开连接的DB client。
        '''
        if clienttype.lower() == 'mysql':
            dbclient = DBCLientMySql(**kwargs)
            # 建立数据库连接。
            dbclient.connect()
        elif clienttype.lower() == 'postgresql':
            dbclient = DBCLientPGSql(**kwargs)
            dbclient.connect()
        else:
            dbclient = DBClientSQLite()
            dbclient.connect(**kwargs)

        return dbclient

    def close(self):
        '''
        关闭数据库连接池中的数据库连接。
        '''
        if self._freedDbClientList:
            try:
                for freedDbClient in self._freedDbClientList:
                    freedDbClient.close()
                for usedDbClient in self._usedDbClientList:
                    usedDbClient.close()
            except Exception, e:
                raise ZeusException, _('Failed to close the db manager. Exception: %(exception)s.' % {'exception':str(e)})

dm = DbMgr()
