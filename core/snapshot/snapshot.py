#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import os
import datetime
from core.exception.DarkException import DarkException
from core.output.logging import logger
from core.directory.localDir import get_local_dir
from i18n import _

SNAPSHOT_DIR = os.path.join(get_local_dir() + os.path.sep \
                            + str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')))


class Snapshot():
    def __init__(self):
        self.snapshotDir = SNAPSHOT_DIR
        self.create_snapshot_dir()

    def get_snapshot_dir(self):
        return SNAPSHOT_DIR

    def create_snapshot_dir(self):
        '''
        描述： 创建home目录。
        @return: boolean
        '''
        if not os.path.exists(self.snapshotDir):
            try:
                os.makedirs(self.snapshotDir)
            except OSError:
                return False
        return True

    def store_snapshot(self, fileName, fileText):
        filePath = self.snapshotDir + os.path.sep + fileName.replace('/', '_') + '.html'
        try:
            htmlFile = open(filePath, 'w')
            htmlFile.write(fileText)
            htmlFile.close()
        except Exception, e:
            import traceback
            raise DarkException, _('Store snapshot filed, place check it! Exception: %s' + traceback.format_exc())
            # 输入日志

sp = Snapshot()

if __name__ == '__main__':
    url = "http://www.baidu.com/index"
    sp = Snapshot()
    dirs = os.listdir(get_local_dir())
    for dir in dirs:
        print dir
    for i in range(10):
        print i
    sp.store_snapshot('www.baidu.com/index', 'this is baidu, test')