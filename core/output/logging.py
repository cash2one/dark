#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import Queue
import functools
import threading

POISON_PILL = -1
start_lock = threading.Lock()


def start_thread_on_demand(func):
    """
    根据需要启动日志线程
    """
    def od_wrapper(*args, **kwds):
        global start_lock
        with start_lock:
            if not logger.is_alive():
                logger.start()
        return func(*args, **kwds)
    return od_wrapper


class Logger(threading.Thread):
    """
    日志模块，输出程序产生的debug,info,error,notice日志信息
    """

    methods = (
        'debug',
        'info',
        'error',
        'notice'
    )

    def __init__(self):
        #threading.Thread.__init__(self)
        super(Logger, self).__init__()
        self.inQueue = Queue.Queue()
        self.running = threading.Event()       # 工厂化的线程事件，可通过set方法去设置管理标志为True，而用clear方法设置管理标志为False
        self.running.set()

    def _addToQueue(self, *args):
        '''
        描述： 将要输出的数据加入到队列中
        @:parameter args: 要输出的数据
        :return:
        '''
        self.inQueue.put(args)

    def setOutputPlugin(self, plugin):
        '''
        描述： 设置输出插件，选择要使用的输出方式
        @:parameter plugin: 要输出的插件类型
        :return:
        '''
        self.outputPlugin = plugin

    def finOutputPlugin(self):
        '''
        描述： 完成输出插件的使用，将其关闭
        :return:
        '''
        self.outputPlugin.close()

    def _callOutputAction(self, args):
        '''
        描述： 调用插件输出行为，将要输出的信息格式化后推送
        @:parameter args: 要输出的信息
        :return:
        '''
        encoded_params = []

        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8', 'replace')

            encoded_params.append(arg)

        encoded_params[0] = encoded_params[0].upper()
        args = tuple(encoded_params)

        self.outputPlugin.output(args)

    def endLogging(self):
        '''
        描述： 完成日志记录，关闭日志输出插件
        :return:
        '''
        self.inQueue.put(POISON_PILL)

        while self.running.isSet():
            time.sleep(1)
        self.finOutputPlugin()       # 关闭一些必要的插件句柄，如file.close等

    def run(self):
        '''
        描述： 运行日志输出， 打印日志
        :return:
        '''
        # 依次从队列中取出信息进行操作，直到队列中读取的信息为-1，表示队列中没有信息
        while True:
            work_unit = self.inQueue.get()      # 获取一个任务单元

            if work_unit == POISON_PILL:
                self.running.clear()            # 当任务都执行完成的时候关闭任务管理
                break

            else:
                self._callOutputAction(work_unit)   # 当存在任务时候，调用任务执行输出
                self.inQueue.task_done()            # 表明当前任务的完成

    @start_thread_on_demand
    def __getattr__(self, method):
        """
        返回函数_add_to_queue（'debug',...）
        """
        if method in self.methods:
            # 偏函数，相当于常见一个method方法的任务去加入queue。
            # eg: method = debug, 则相当于 addToQueue(debug)
            # eg: method = info, 则相当与addToQueue(info)
            return functools.partial(self._addToQueue, method)
        else:
            raise AttributeError("'Logger' object has no attribute '%s'"
                                 % method)

logger = Logger()

if __name__ == '__main__':
    import random
    for i in range(1, 60):
        t = random.randrange(10, 100, 2)
        logger.debug("test %d" %t)

    logger.endLogging()


