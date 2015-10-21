# -*- coding: utf-8 -*-
import os
import sys
import time

filePath = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-4])
sys.path.append(filePath)

def test1():
    #f = open('1.txt', 'a')
    #f.write('1\n')
    #f.close()
    time.sleep(0.1)
    print '1\n'

def test2():
    #f = open('1.txt', 'a')
    #f.write('2\n')
    #f.close()
    time.sleep(0.1)
    print '2\n'

def test3():
    #f = open('1.txt', 'a')
    #f.write('3\n')
    #f.close()
    time.sleep(0.1)
    print '3\n'


def test4():
    #f = open('1.txt', 'a')
    #f.write('4\n')
    #f.close()
    time.sleep(0.1)
    print '4\n'

def test5():
    #f = open('1.txt', 'a')
    #f.write('5\n')
    #f.close()
    time.sleep(0.1)
    print '5\n'

def test6():
    import pdb
    pdb.set_trace()
    #f = open('1.txt', 'a')
    #f.write('6\n')
    #f.close()
    print '6\n'

if __name__ == '__main__':
    from core.threads.threadManager import ThreadManager
    tm = ThreadManager()
    i = 100
    while i:
        tm.startTask(test1)
        tm.startTask(test2)
        tm.startTask(test3)
        tm.startTask(test4)
        tm.startTask(test5)
        i -= 1

    tm.join()
    #tm.startTask(test6)


