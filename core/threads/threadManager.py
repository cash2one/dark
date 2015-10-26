# -*- coding: utf-8 -*-
'''
threadManager.py

Author: peta
Date: 20150925

线程管理。
'''
from core.threads.threadPool import ThreadPool, WorkTask
from core.settings.settings import settings


class ThreadManager(object):
    '''
    管理线程。
    '''
    def __init__(self):
        self._initialized = False
        self._initPool()

    def _initPool(self):
        if not self._initialized:
            self._maxThreads = settings.getint('THREAD_MAX') or 5
            self._queueSize = settings.getint('QUEUE_SIZE') or 200
            self._threadPool = ThreadPool(self._queueSize, self._maxThreads)
            self._initialized = True

    def startTask(self, target, args=(), kwds={}):
        task = WorkTask(target, args=args, kwds=kwds)
        self._threadPool.putWorkTask(task)

    def join(self):
        self._threadPool.join()

    def setMaxThreads(self, max):
        if self._maxThreads > max:
            self._threadPool.dissmissWorkThreads(self._maxThreads - max)
        elif self._maxThreads < max:
            self._threadPool.createWorkThreads(max - self._maxThreads)
        self._maxThreads = max

    def getMaxThreads(self):
        if not self._initialized:
            self._initPool()
        return self._maxThreads

tm = ThreadManager()
