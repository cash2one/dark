#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

from shutil import rmtree
from urlparse import urlparse
#from log.output import output

import os
import time


class Snapshot:
    def __init__(self):
        self.dirPath = None

    def set_snapshot_path(self, path):
        self.dirPath = path

    def create_snapshot_dir(self):
        if not os.path.exists(self.dirPath):
            try:
                os.makedirs(self.dirPath)
            except Exception, e:
                print 'Snapshot.create_snapshot_dir %s' % e
                output.error('Snapshot.create_snapshot_dir %s' % e)
                import traceback
                traceback.print_exc()
        else:
            print u'The directory: %s had been made!' % self.dirPath

    def get_snapshot(self, fileName, fileText):
        if os.path.exists(self.dirPath):
            fileRealPath = os.path.join(self.dirPath, fileName)
            if not os.path.exists(fileRealPath):
                try:
                    htmlFile = file(fileRealPath, 'w')
                    htmlFile.write(fileText)
                    htmlFile.close()
                except Exception, e:
                    print 'Snapshot.get_snapshot %s' % e
                    output.error('Snapshot.get_snapshot %s' % e)
                    import traceback
                    traceback.print_exc()
            else:
                print u'The file: %s had been exists!' % fileName
        else:
            print u'The directory: %s not exists!' % self.dirPath

    def clear_snapshot_dir(self):
        if os.path.exists(self.dirPath):
            try:
                rmtree(self.dirPath)
            except Exception, e:
                print 'Snapshot.clear_snapshot_dir %s' % e
                output.error('Snapshot.clear_snapshot_dir %s' % e)
                import traceback
                traceback.print_exc()
        else:
            print u'The directory: %s not exists!' % self.dirPath

    def clear_snapshot(self, fileName):
        if os.path.exists(self.dirPath):
            fileRealPath = os.path.join(self.dirPath, fileName)
            if os.path.exists(fileRealPath):
                try:
                    os.remove(fileRealPath)
                except Exception, e:
                    print 'Snapshot.clear_snapshot %s' % e
                    output.error('Snapshot.clear_snapshot %s' % e)
                    import traceback
                    traceback.print_exc()
            else:
                print u'The file: %s not exists!' % fileName
        else:
            u'The directory: %s not exists!' % self.dirPath


if __name__ == '__main__':
    ISOTIMEFORMAT = '%Y_%m_%d'
    DIRECTORYNAME = 'snapshot'

    url = "http://www.baidu.com"
    dir = os.path.join(os.getcwd(), DIRECTORYNAME)
    dirPath = os.path.join(dir, urlparse(url).netloc)
    time = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
    newPath = os.path.join(dirPath, time)
    newPath2 = os.path.join(dirPath, "2015_09_12")

    snap = Snapshot()
    snap.set_snapshot_path(newPath)
    snap2 = Snapshot()
    snap2.set_snapshot_path(newPath2)
    path2 = snap2.create_snapshot_dir()
    path1 = snap.create_snapshot_dir()
    snap.get_snapshot('b.txt', 'this is baidu!')
    snap.get_snapshot('a.txt', 'this is google!')

