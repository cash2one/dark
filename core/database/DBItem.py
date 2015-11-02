#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mysqlDBClient import DBClientMySql
from core.exception.DarkException import DarkException
from core.settings.settings import settings
from core.profile.profile import pf
from i18n import _


def make_two_item_tuple(column, value):
    """
    描述： 将列名字和value生成为一个tuple元素
    """
    return (column, value)


def make_three_item_tuple(column, value, opreator='='):
    """
    描述： 将列名字、value与操作连接符生成为一个tuple元素
    """
    return (column, value, opreator)


class DBItem(object):
    def __init__(self):
        self.dbClient = DBClientMySql(**pf.getDbInfo())  # 通过配置文件设置当前数据库的user,password,db

    def init(self):
        self.dbClient.connect()

    def create_table_and_index(self):
        with self.dbClient._dbLock:
            tablename = self.get_table_name()
            primarykey = self.get_primary_key_columns()
            index = self.get_index_columns()
            column = self.get_columns()
            try:
                self.dbClient.createTable(tablename, column, primarykey)
                self.dbClient.createIndex(tablename, index)
            except Exception, e:
                raise DarkException, _('Failed to create table or index. Exception: %(exception)s.' % {'exception': str(e)})

    def end(self):
        """
        完成操作
        """
        self.dbClient.disconnect()

    def set_table_name(self, table):
        self._DATA_TABLE = table

    def get_table_name(self):
        return self._DATA_TABLE

    def set_columns(self, columnList):
        self._COLUMNS = columnList

    def get_columns(self):
        return self._COLUMNS

    def set_primary_key_columns(self, primaryKeyTuple):
        self._PRIMARY_KEY_COLUMNS = primaryKeyTuple

    def get_primary_key_columns(self):
        return self._PRIMARY_KEY_COLUMNS

    def set_index_columns(self, indexTuple):
        self._INDEX_COLUMNS = indexTuple

    def get_index_columns(self):
        return self._INDEX_COLUMNS


class BLItem(DBItem):
    """Represents history item."""

    def __init__(self):
        DBItem.__init__(self)
        self._DATA_TABLE = settings.get("BL_DATA_TABLE")
        self._COLUMNS = settings.get("BL_COLUMNS")
        self._PRIMARY_KEY_COLUMNS = settings.get("BL_PRIMARY_KEY_COLUMNS")
        self._INDEX_COLUMNS = settings.get("BL_INDEX_COLUMNS")

    def find_keyword_in(self, keywordsList):
        if keywordsList:
            for i in range(len(keywordsList)):
                searchData = [make_three_item_tuple(settings.get('BL_SEARCH_WORD'), keywordsList[i])]
                if self.dbClient.find_data(self.get_table_name(), searchData):
                    return True
                else:
                    continue
            return False
        return False

    def store_keyword_in(self, storeList):
        if storeList:
            for i in range(len(storeList)):
                insertData = [make_two_item_tuple(settings.get('BL_STORE_WORD'), storeList[i])]
                searchData = [make_three_item_tuple(settings.get('BL_STORE_WORD'), storeList[i])]
                if not self.dbClient.get_data(self.get_table_name(), searchData):
                    self.dbClient.insert_data(self.get_table_name(), insertData)
                else:
                    pass


class WLItem(DBItem):
    def __init__(self):
        DBItem.__init__(self)
        self._DATA_TABLE = settings.get("WL_DATA_TABLE")
        self._COLUMNS = settings.get("WL_COLUMNS")
        self._PRIMARY_KEY_COLUMNS = settings.get("WL_PRIMARY_KEY_COLUMNS")
        self._INDEX_COLUMNS = settings.get("WL_INDEX_COLUMNS")

    def find_url_in(self, url):
        if url:
            searchData = [make_three_item_tuple(settings.get('WL_SEARCH_WORD'), url)]
            if self.dbClient.find_data(self.get_table_name(), searchData):
                return True
            else:
                return False
        return False

    def store_url_title_in(self, url, title):
        if url:
            insertData = []
            keys = settings.get('WL_STORE_WORD')
            insertData.append(make_two_item_tuple(keys[0], url))
            insertData.append(make_two_item_tuple(keys[1], title))
            self.dbClient.insert_data(self.get_table_name(), insertData, True)


class DTItem(DBItem):
    def __init__(self):
        DBItem.__init__(self)
        self._DATA_TABLE = settings.get("DT_DATA_TABLE")
        self._COLUMNS = settings.get("DT_COLUMNS")
        self._PRIMARY_KEY_COLUMNS = settings.get("DT_PRIMARY_KEY_COLUMNS")
        self._INDEX_COLUMNS = settings.get("DT_INDEX_COLUMNS")

    def store_url_hidden_type_in(self, url, hidden, level, type):
        if url:
            insertData = []
            keys = settings.get('DT_STORE_WORD')
            insertData.append(make_two_item_tuple(keys[0], url))
            insertData.append(make_two_item_tuple(keys[1], hidden))
            insertData.append(make_two_item_tuple(keys[2], level))
            insertData.append(make_two_item_tuple(keys[3], type))
            self.dbClient.insert_data(self.get_table_name(), insertData, False)

class RSItem(DBItem):
    def __init__(self):
        DBItem.__init__(self)
        self._DATA_TABLE = settings.get("RS_DATA_TABLE")
        self._COLUMNS = settings.get("RS_COLUMNS")
        self._PRIMARY_KEY_COLUMNS = settings.get("RS_PRIMARY_KEY_COLUMNS")
        self._INDEX_COLUMNS = settings.get("RS_INDEX_COLUMNS")

    def store_url_hidden_report_in(self, id, refSiteId, threatName, threatLevel, threatSum, statisticTime, reportName):
        insertData = []
        keys = settings.get('RS_STORE_WORD')
        insertData.append(make_two_item_tuple(keys[0], id))
        insertData.append(make_two_item_tuple(keys[1], refSiteId))
        insertData.append(make_two_item_tuple(keys[2], threatName))
        insertData.append(make_two_item_tuple(keys[3], threatLevel))
        insertData.append(make_two_item_tuple(keys[4], threatSum))
        insertData.append(make_two_item_tuple(keys[5], statisticTime))
        insertData.append(make_two_item_tuple(keys[6], reportName))
        self.dbClient.insert_data(self.get_table_name(), insertData, False)


blacklist = BLItem()
whitelist = WLItem()
detectResult = DTItem()
detectReport = RSItem()

blacklist.init()
whitelist.init()
detectResult.init()
detectReport.init()
