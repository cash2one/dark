#!/usr/bin/env python
# -*- coding: utf-8 -*-


def dark_start(target):
    from dark_core.database.mysqlManger import sqlMg
    from hiddenDetect import hiddenlink_obj
    from dark_core.output.console import consoleLog
    from dark_core.output.textFile import fileLog
    from dark_core.output.logging import logger
    from dark_core.profile.profile import pf
    from dark_core.settings.settings import settings
    from dark_core.parser.urlParser import url_object
    from datetime import datetime

    # 设置日志模块
    if pf.getLogType() == 'True':
        file_path = settings.get('LOG_FILE_PATH')
        datetimestrf = datetime.now().strftime('%Y-%m-%d')
        domain = url_object(target).getRootDomain                   # 获取当前页面的根域名
        file_name = file_path + domain + '_' + datetimestrf + '.log'# 检测文件名按域名_时间.log的形式加载
        fileLog.set_file_name(file_name)                            # 设置日志文件名
        logger.setOutputPlugin(fileLog)
    else:
        logger.setOutputPlugin(consoleLog)

    # 执行检测
    hidden = hiddenlink_obj(target)
    hidden.init()
    hidden.run()
    hidden.finsh()

    # 关闭相关数据库的连接和日志打印模块
    sqlMg.dispose()
    logger.endLogging()

if __name__ == '__main__':
    url = 'http://www.baidu.com'
    dark_start(url)
