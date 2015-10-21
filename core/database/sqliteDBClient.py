#!/usr/bin/env python
# -*- coding: utf-8 -*-
from DBClient import DBClient


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
            self._db = sqlite3.connect(filenameUtf8, check_same_thread=False)  # @UndefinedVariable
            self._db.text_factory = str  # 将设置sqlite的显示为bytestring模式
        except Exception, e:
            raise darkManagerException('Failed to create the database in file "%s". Exception: %s' % (filenameUtf8, e))