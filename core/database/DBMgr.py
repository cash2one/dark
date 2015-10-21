#!/usr/bin/env python
# -*- coding: utf-8 -*-


class DbMgr(object):
    '''
    单例数据库连接池管理器。
    '''

    def __init__(self):
        _class = self.__class__
        if _class._do_init_:
            # 连接池大小。
            self._poolsize = 10
            # 信号量，用于控制对共享资源进行访问的线程数量。
            self._semaphore = threading.BoundedSemaphore(self._poolsize)
            # 列表，用于存放空闲的数据库连接。
            self._free_db_list = []
            # 用于记录正在使用的数据库连接数目。
            self._checked_out = 0
            self._db = None
            _class._do_init_ = False

    def __new__(cls):
        '''
        这个方法真正实现了单例模式。
        '''
        _dbmgrstr = '_dbmgr_instance'
        if not cls.__dict__.get(_dbmgrstr):
            setattr(cls, _dbmgrstr, object.__new__(cls))
            cls._do_init_ = True
        return getattr(cls, _dbmgrstr)

    def executeSql(self, sql, params=[], commit_urg=False):
        '''
        执行SQL语句，主要是执行DDL、DCL、DML。

        @param sql: 参数化SQL语句。
        @param params: 参数值列表或元组。
        '''
        return self.process_request('executeSql', sql, parameters=params, commit_urg=commit_urg)

    def retrieveRows(self, sql, params=[], all=False):  # @ReservedAssignment
        '''
        执行SQL语句提取数据行，主要是执行DQL。

        @param sql: 参数化SQL语句。
        @param params: 参数值列表或元组。
        @return: 返回查询结果，列表或元组（取决于数据库）。
        '''
        return self.process_request('retrieveRows', sql, parameters=params, all=all)

    def callProcedure(self, name, params=[]):
        '''
        执行存储过程。

        @param name: 存储过程名称。
        @param params: 存储过程参数列表或元组。
        '''
        return self.process_request('callProcedure', name, parameters=params)

    def set_pool_size(self, size=10):
        '''
        设置连接池的大小。

        @param size: 待设置连接池大小，默认是10。
        '''
        # 处理萎缩池。
        if self._poolsize <= size:
            pass
        else:
            length = len(self._free_db_list)
            if length + self._checked_out <= size:
                pass
            else:
                count = length + self._checked_out - size
                if count <= length:
                    self._free_db_list = self._free_db_list[count:]
                else:
                    import time
                    time.sleep(0.5)
                    self.set_pool_size(size)

        self._poolsize = size
        self._semaphore = threading.BoundedSemaphore(size)

    def process_request(self, method, *args, **kwargs):
        '''
        提交一个到可用数据库client的请求，并调用相应client的方法。

        @param method: 数据库client方法名。
        @param *args: method的位置参数。
        @param **kwargs: method的关键字参数。
        @return: 返回数据client方法调用的结果。
        '''
        theclient = self._get_avail_dbclient()
        if theclient:
            try:
                return getattr(theclient, method)(*args, **kwargs)
            finally:
                self._free_dbclient(theclient)
        else:
            raise Exception('All %d database connections are busy.' % self._poolsize)

    def _get_avail_dbclient(self):
        '''
        私有方法，从连接池返回一个可用的DB client，如果没有，则返回None。
        '''
        retry_count = 0
        theclient = None

        while retry_count < 20:
            if self._semaphore.acquire():
                if self._free_db_list:
                    # 取第一个以循环使用。
                    theclient = self._free_db_list.pop(0)
                else:
                    theclient = self._create_dbclient(profile.getDbType(), **profile.getDbInfo())
            if theclient:
                self._checked_out += 1
                break
            else:
                retry_count += 1
                import time
                time.sleep(0.2)

        return theclient

    def _free_dbclient(self, theclient):
        '''
        释放DB client并存放于列表最后面，以循环使用。

        @param theclient: DB client。
        '''
        self._free_db_list.append(theclient)
        self._checked_out -= 1
        self._semaphore.release()

    def _create_dbclient(self, clienttype, **kwargs):
        '''
        返回一个DB client。

        @param clienttype: 数据库client类型，如'mysql'。
        @param **kwargs: 关键字参数，用于创建数据库client对象。
        @return: 返回一个打开连接的DB client。
        '''
        if clienttype.lower() == 'mysql':
            DB = DBClientMySql(**kwargs)
            # 建立数据库连接。
            DB.connect()
        elif clienttype.lower() == 'postgresql':
            DB = DBCLientPGSql(**kwargs)
            DB.connect()
        else:
            DB = DBClientSQLite()
            DB.connect(**kwargs)

        self._db = DB
        return DB

    def close(self):
        '''
        关闭数据库连接池中的数据库连接
        '''
        if self._db:
            try:
                self._db.close()
            except Exception, e:
                output.debug("Exception occurs when shutting down DB_Pool: %s" % str(e))

dbm = DbMgr()