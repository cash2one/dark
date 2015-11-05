#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import os
import codecs
from core.exception.DarkException import DarkException
from core.settings.settings import settings
from core.parser.urlParser import url_object
from i18n import _


class Snapshot():
    def __init__(self, url):
        self.url = url  # 要加载快照生成快照的组件名
        self.target = self.url.replace('/', '_')
        self.root_target = url_object(self.url).getDomain
        self.snapshot_path = settings.get('SNAPSHOT_PAHT')

        self._file_name = self.target + '_snapshot.html'
        self._file_path = os.path.join(self.snapshot_path, self._file_name)     # eg:/tmp/www.kingboxs.com_aaa_snapshot.html

        self._initialized = False  # 初始化标志

    def _init(self):
        self._initialized = True
        try:
            self._file = codecs.open(self._file_path, "w", "utf-8", 'replace')
        except IOError, io:
            msg = 'Can\'t open snapshot file "' + os.path.abspath(self._file_path) + '" for writing'
            msg += ': "%s".' % io
            raise DarkException(msg)
        except Exception, e:
            msg = 'Can\'t open snapshot file ' + self._file_path + ' for output.'
            msg += ' Exception: "' + str(e) + '".'
            raise DarkException(msg)

    def store_snapshot(self, content):
        if not self._initialized:
            self._init()
            try:
                self._file.write(content)
            except Exception, e:
                raise DarkException, _('Store Write html content to snapshot failed! Please check it! Exception: ', e)
            finally:
                self._file.close()
        else:
            self._file.close()

        import shutil

        dir = self.root_target
        fin_dir = os.path.join(self.snapshot_path, dir)     # eg: /tmp/www.kingboxs.com
        fin_sp_dir = os.path.join(fin_dir, 'snapshot')
        fin_path = os.path.join(fin_sp_dir, self._file_name)

        if not os.path.exists(fin_sp_dir):
            os.makedirs(fin_sp_dir)

        try:
            shutil.move(self._file_path, fin_path)
        except Exception, e:
            raise DarkException, _('Move snapshot file to destination directory failed! Please check it! Exception: %s' % e)

if __name__ == '__main__':
    url = 'http://www.kingboxs.com/index.php?case=archive&act=search'
    sp = Snapshot(url)
    sp.store_snapshot('aaa')
    url2 = 'http://www.kingboxs.com/index.php?case=special&act=show&spid=1'
    sp2 = Snapshot(url2)
    sp2.store_snapshot('aaa')
