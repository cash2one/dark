#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'
import re
import jieba
import jieba.analyse
from math import sqrt
from core.exception.DarkException import DarkException
from i18n import _


class content_obj:
    def __init__(self):
        pass

    def compair_string_by_cos(self, content1, content2):
        """
        描述： 通过余弦定理去判断两个文本是否是相似的
        :param content1: 传入的第一个文本
        :param content2: 传入的第二个文本
        :return:rate，如果该值等于0.0则表示完全不相似
        """
        _curContentWord = {}        # 记录当前文本中提取出来的词语
        _accepteChars = re.compile(u"[\u4e00-\u9fa5]+|[a-zA-Z]+")     # 正则匹配接收到的词语是否为中文或者英文字符          # 正则匹配接受到的
        try:
            segList = jieba.cut(content1, cut_all=True)      # 对内容1进行分词
            for item in segList:
                if _accepteChars.match(item) is not None:
                    if item not in _curContentWord.keys():
                        _curContentWord[item] = [1,0]
                    else:
                        _curContentWord[item][0] += 1
        except Exception, e:
            raise DarkException, _('Failed to cut the words. Exception: %(exception)s.' % {'exception': str(e)})

        try:
            segList = jieba.cut(content2, cut_all=True)      # 对内容2进行分词
            for item in segList:
                if _accepteChars.match(item) is not None:
                    if item not in _curContentWord.keys():
                        _curContentWord[item] = [0,1]       # 注意此处，内容2的维度和内容一不同
                    else:
                        _curContentWord[item][1] += 1
        except Exception, e:
            raise DarkException, _('Failed to cut the words. Exception: %(exception)s.' % {'exception': str(e)})


        sum = 0
        sumA = 0
        sumB = 0
        rate = 0.0      # 存储最终的cos值

        for word in _curContentWord.values():
            sum += word[0] * word[1]
            sumA += word[0]**2
            sumB += word[1]**2

        try:
            rate = sum / (sqrt(sumA * sumB))
        except ZeroDivisionError:
            pass
        except Exception, e:
            DarkException, _('Failed to get rate. Exception: %(exception)s.' % {'exception': str(e)})
        return rate


    def get_key_words_by_all(self, content, topK=5):
        """
        描述： 通过两种方式获取当前内容的关键字
        :param content: 传入的文本
        :param topK: 要提取关键字的个数, 此处应为用了两个方法，获得的关键字实际大于指定个数
        :return: tags获取的关键字列表
        """
        tags = []
        try:
            tags1 = jieba.analyse.extract_tags(content, topK=topK)
            tags2 = jieba.analyse.textrank(content, topK=topK)
            tags = set(tags1) | set(tags2)
        except Exception, e:
            DarkException, _('Failed to get keywords by two functions. Exception: %(exception)s.' % {'exception': str(e)})
        return list(tags)


    def get_key_words_by_TF_IDF(self, content, topK=5):
        tags = jieba.analyse.extract_tags(content, topK=topK)
        return tags

    def get_key_words_by_TextRank(self, content, topK=5):
        tags = jieba.analyse.textrank(content, topK=topK)
        return tags

    def convert_to_string(self, list, separator=','):
        return separator.join(list)

if __name__ == '__main__':
    keyword = content_obj()
    s = ''
    list1 = keyword.get_key_words_by_TF_IDF(s)
    print list1
    list2 = keyword.get_key_words_by_TextRank(s)
    print list2
    list3 = keyword.get_key_words_by_all(s)
    print list3
    print keyword.convert_to_string(list3)

    s1 = "山西粮网-太原国家粮食交易中心 山西粮网,太原国家粮食交易中心 山西粮网-太原国家粮食交易中心"
    s2 = "就业指南网 就业指南网 - 公务员考试|事业单位招聘|高等院校招聘|中小学招聘|知名企业招聘|招聘会信息 就业指南网,2014年,2015年,公务员考试,事业单位招聘,高等院校招聘,中小学招聘,知名企业招聘,招聘会信息 就业指南网：为您提供最新的公务员考试,事业单位招聘,高等院校招聘,中小学招聘,知名企业招聘,招聘会信息"
    print keyword.compair_string_by_cos(s1, s2)