# -*- coding: utf-8 -*-
'''
threadPool.py

Author: peta
Date: 20150916

线程池。
'''
import Queue
import threading
import traceback

from i18n import _


class WorkThread(threading.Thread):
    '''
    工作线程, 后台运行。 
    
    不间断从任务队列取任务执行，直到线程被告知退出。
    '''
    def __init__(self, tasksQueue, semaphoreCustomer, semaphoreProducer, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(1)
        self._tasksQueue = tasksQueue
        #om.debug(_('[threadPool] Init with task queue %(id)s.') % {'id':id(self._tasksQueue)})
        self._dissmissed = threading.Event() # 线程是否结束运行的事件
        self._semaphoreCustomer = semaphoreCustomer # 任务队列消费者信号量
        self._semaphoreProducer = semaphoreProducer # 任务队列生产者信号量
        self.start()
    
    def run(self):
        '''
        不间断处理任务直到被告知退出。
        '''
        while not self._dissmissed.isSet():
            if self._semaphoreCustomer.acquire(): # 消费者P操作
                try:
                    task = self._tasksQueue.get(timeout=1) # 阻塞1秒
                except:
                    # 正常应该永远不会运行到此
                    #om.debug(_('[threadPool] Blocking at tasks queue get. Size: %(size)s.')
                              #% {'size':str(self._tasksQueue.qsize())})
                    self._semaphoreCustomer.release()
                    continue

                #om.debug(_('[threadPool] Unblocking after tasks queue get.'))
                #om.debug(_('[threadPool] The tasks queue size for thread with id %(id)s is %(size)s.')
                          #% {'id':str(id(self)), 'size':str(self._tasksQueue.qsize())})

                try:
                    task.callable(*task.args, **task.kwds)
                    self._tasksQueue.task_done()
                except:
                    #om.error(_('[threadPool] The thread: %(thread)s raised an exception while running the task: %(callable)s')
                              #% {'thread':self, 'callable':task.callable})
                    #om.error(_('[threadPool] Exception: %(exception)s.') % {'exception':traceback.format_exc()})
                    self._semaphoreProducer.release() # 生产者V操作
                else:
                    self._semaphoreProducer.release() # 生产者V操作

        #om.debug(_('[threadPool] Ending!'))

    def dismiss(self):
        '''
        通知线程结束运行。
        '''
        self._dissmissed.set()

class WorkTask(object):
    '''
    表示一个任务。
    '''
    def __init__(self, callable, args=None, kwds=None):
        '''
        构造函数。

        @:parameter callable: 可调用对象。
        @:parameter args: 可调用对象的位置参数。
        @:parameter kwds: 可调用对象的关键字参数。
        '''
        self.callable = callable
        self.args = args or []
        self.kwds = kwds or {}

class ThreadPool(object):
    '''
    线程池，维护多个工作线程。
    '''
    def __init__(self, queueSize, poolSize):
        _class = self.__class__
        if _class._doInit:
            self._queueSize = queueSize
            self._poolSize = poolSize
            self._semaphoreCustomer = threading.Semaphore(0) # 默认0
            self._semaphoreProducer = threading.Semaphore(self._queueSize) # 默认队列大小
            self._tasksQueue = Queue.Queue(self._queueSize)
            #om.debug(_('[threadPool] %(poolId)s init with tasks queue %(queueId)s.')
                      #% {'poolId':id(self), 'queueId':id(self._tasksQueue)})
            self._workThreads = []
            self.createWorkThreads(self._poolSize)
            _class._doInit = False

    def __new__(cls, queueSize, poolSize):
        _pool = '_poolInstance'
        if not cls.__dict__.get(_pool):
            setattr(cls, _pool, object.__new__(cls, queueSize, poolSize))
            cls._doInit = True
        return getattr(cls, _pool)

    def createWorkThreads(self, num):
        for i in xrange(num):
            self._workThreads.append(WorkThread(self._tasksQueue, self._semaphoreCustomer, self._semaphoreProducer))
    
    def dismissWorkThreads(self, num):
        for i in xrange(min(num, len(self._workThreads))):
            workThread = self._workThreads.pop()
            workThread.dismiss()

    def putWorkTask(self, task):
        if self._semaphoreProducer.acquire(): # 生产者P操作
            self._tasksQueue.put(task)
            #om.debug(_('[threadPool] Successfully added task to tasks queue. The queue size: %(size)s.') %
                         #{'size':self._tasksQueue.qsize()})
            self._semaphoreCustomer.release() # 消费者V操作

    def join(self):
        self._tasksQueue.join() # 等到队列为空，再进行别的操作
        self.dismissWorkThreads(len(self._workThreads))
