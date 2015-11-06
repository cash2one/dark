#!/usr/bin/env python
# -*- coding: utf-8 -*-

def dark_start(target, id):
    from core.database.DBItem import detectResult, blacklist, whitelist, detectReport
    from hiddenDetect import hiddenlink_obj
    from core.output.console import consoleLog
    from core.output.textFile import fileLog
    from core.output.logging import logger
    from core.profile.profile import pf

    # 设置日志模块
    if pf.getLogType() == 'True':
        logger.setOutputPlugin(fileLog)
    else:
        logger.setOutputPlugin(consoleLog)

    # 执行检测
    hidden = hiddenlink_obj(target, id)
    hidden.init()
    hidden.run()
    hidden.finsh()

    # 关闭相关数据库的连接和日志打印模块
    blacklist.end()
    whitelist.end()
    detectReport.end()
    detectResult.end()
    logger.endLogging()

if __name__ == '__main__':
    url = 'http://www.baidu.com'
    dark_start(url,0)
