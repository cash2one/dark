#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jason'

import re
from core.parser.htmlParser import html_object
from core.settings.settings import settings

class Checker:
    def __init__(self, object):
        self.htmlParser = object

    '''
    描述： 检测颜色是否不可见
    '''

    def is_color_hidden(self, element):
        # 1. 获取当前元素的父类中的背景色
        bgColor = None
        aColor = None
        fontColor = None
        parent = self.htmlParser.get_all_parent_element(element)
        for elem in parent:
            color = self.htmlParser.get_element_style_attr_value(elem, 'background-color')
            if color is not None:
                bgColor = color.lower()
                break
        # 2. 获取当前元素的字体颜色
        color = self.htmlParser.get_element_style_attr_value(element, 'color')
        if color is not None:
            aColor = color.lower()
        # 3. 获取当前元素的子元素的字体颜色
        children = self.htmlParser.get_all_child_element(element)
        for elem in children:
            if elem.tag == 'font' and 'color' in elem.keys():
                fontColor = elem.get('color').lower()
                break
        if bgColor is None:
            if aColor == '#ffffff' or fontColor == '#ffffff':
                return True
        else:
            if aColor == bgColor or fontColor == bgColor:
                return True
        return False

    '''
    描述： 检测字体大小小于可见大小
    '''

    def is_font_size_hidden(self, element):
        fontSize = None
        # 1. 获取自身的font-size大小
        size = self.htmlParser.get_element_style_attr_value(element, 'font-size')
        if size is not None:
            fontSize = size.lower()
        else:
            # 2. 获取父类中的font-size大小
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                size = self.htmlParser.get_element_style_attr_value(elem, 'font-size')
                if size is not None:
                    fontSize = size
                    break
        if fontSize is not None:
            match = re.search(r'([-]?\d+)\s*(\D+)', fontSize, re.IGNORECASE)
            if match is not None:
                if match.group(2).lower() == 'px' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('FONT_SIZE'):
                    return True
                elif match.group(2).lower() == 'em' \
                        and match.group(1).isdigit() \
                        and (float(match.group(1)) * 10) <= settings.getfloat('FONT_SIZE'):
                    return True
                elif match.group(2) == '%' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('FONT_SIZE_PERCENT'):
                    return True
                else:
                    return False
        return False

    '''
    描述： 检测字体行高小于可见大小
    '''

    def is_line_height_hidden(self, element):
        fontHeight = None
        # 1. 获取自身的font-size大小
        height = self.htmlParser.get_element_style_attr_value(element, 'line-height')
        if height is not None:
            fontHeight = height.lower()
        else:
            # 2. 获取父类中的font-size大小
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                size = self.htmlParser.get_element_style_attr_value(elem, 'line-height')
                if size is not None:
                    fontHeight = size
                    break
        if fontHeight is not None:
            match = re.search(r'([-]?\d+)\s*(\D+)', fontHeight, re.IGNORECASE)
            if match is not None:
                # print '%s'%match.group(0)
                # print '%s'%match.group(1)
                # print '%s'%match.group(2)
                if match.group(2).lower() == 'px' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('LINE_HEIGHT'):
                    return True
                elif match.group(2).lower() == 'em' \
                        and match.group(1).isdigit() \
                        and (float(match.group(1)) * 10) <= settings.getfloat('LINE_HEIGHT'):
                    return True
                elif match.group(2) == '%' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('LINE_HEIGHT_PERCENT'):
                    return True
                else:
                    return False
        return False

    '''
    描述： 检测top是否在可视范围外
    '''

    def is_position_top_hidden(self, element):
        posString = None
        topSize = None
        # 1. 获取自身的position、top值
        position = self.htmlParser.get_element_style_attr_value(element, 'position')
        top = self.htmlParser.get_element_style_attr_value(element, 'top')
        if position is not None and top is not None:
            posString = position
            topSize = top
        else:
            # 2.获取父类中的position、top值
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                position = self.htmlParser.get_element_style_attr_value(elem, 'position')
                top = self.htmlParser.get_element_style_attr_value(elem, 'top')
                if position is not None and top is not None:
                    posString = position
                    topSize = top
                    break
        if posString is not None and topSize is not None:
            if posString.lower() == 'absolute' or posString.lower() == 'fixed':
                matchNormal = re.search(r'([-]?\d+)\s*(\D+)', topSize, re.IGNORECASE)
                matchChange = re.search(r'expression_r\(((\d+-)?\d+)\)', topSize, re.IGNORECASE)
                if matchChange is not None:
                    if eval(matchChange.group(1)) <= settings.getfloat('POSITION_TOP'):
                        return True
                    else:
                        return False
                elif matchNormal is not None:
                    if matchNormal.group(2).lower() == 'px' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('POSITION_TOP'):
                        return True
                    elif matchNormal.group(2).lower() == 'em' \
                            and matchNormal.group(1).isdigit() \
                            and (float(matchNormal.group(1)) * 10) <= settings.getfloat('POSITION_TOP'):
                        return True
                    elif matchNormal.group(2) == '%' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('POSITION_TOP_PERCENT'):
                        return True
                    else:
                        return False
                else:
                    return False
        return False

    '''
    描述： 检测left是否在可视范围外
    '''

    def is_position_left_hidden(self, element):
        posString = None
        leftSize = None
        # 1. 获取自身的position、left值
        position = self.htmlParser.get_element_style_attr_value(element, 'position')
        left = self.htmlParser.get_element_style_attr_value(element, 'left')
        if position is not None and left is not None:
            posString = position
            leftSize = left
        else:
            # 2.获取父类中的position、left值
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                position = self.htmlParser.get_element_style_attr_value(elem, 'position')
                left = self.htmlParser.get_element_style_attr_value(elem, 'left')
                if position is not None and left is not None:
                    posString = position
                    leftSize = left
                    break
        if posString is not None and leftSize is not None:
            if posString.lower() == 'absolute' or posString.lower() == 'fixed':
                matchNormal = re.search(r'([-]?\d+)\s*(\D+)', leftSize, re.IGNORECASE)
                matchChange = re.search(r'expression_r\(((\d+-)?\d+)\)', leftSize, re.IGNORECASE)
                if matchChange is not None:
                    if eval(matchChange.group(1)) <= settings.getfloat('POSITION_LEFT'):
                        return True
                    else:
                        return False
                elif matchNormal is not None:
                    if matchNormal.group(2).lower() == 'px' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('POSITION_LEFT'):
                        return True
                    elif matchNormal.group(2).lower() == 'em' \
                            and matchNormal.group(1).isdigit() \
                            and (float(matchNormal.group(1)) * 10) <= settings.getfloat('POSITION_LEFT'):
                        return True
                    elif matchNormal.group(2) == '%' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('POSITION_LEFT_PERCENT'):
                        return True
                    else:
                        return False
                else:
                    return False
        return False

    '''
    描述： 检测text-indent是否在可视范围外
    '''

    def is_text_indent_hidden(self, element):
        indentSize = None
        # 1. 获取自身的position、left值
        indent = self.htmlParser.get_element_style_attr_value(element, 'text-indent')
        if indent is not None:
            indentSize = indent
        else:
            # 2.获取父类中的position、left值
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                indent = self.htmlParser.get_element_style_attr_value(elem, 'text-indent')
                if indent is not None:
                    indentSize = indent
                    break
        if indentSize is not None:
            match = re.search(r'([-]?\d+)\s*(\D+)', indentSize, re.IGNORECASE)
            if match is not None:
                if match.group(2).lower() == 'px' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('TEXT_INDENT'):
                    return True
                elif match.group(2).lower() == 'em' \
                        and match.group(1).isdigit() \
                        and (float(match.group(1)) * 10) <= settings.getfloat('TEXT_INDENT'):
                    return True
                elif match.group(2) == '%' \
                        and match.group(1).isdigit() \
                        and float(match.group(1)) <= settings.getfloat('TEXT_INDENT_PERCENT'):
                    return True
                else:
                    return False
        return False

    '''
    描述： 检测marquee是否在可视范围外
    '''

    def is_marquee_value_hidden(self, element):
        # 1. 获取父类的标签属性
        parent = self.htmlParser.get_all_parent_element(element)
        for elem in parent:
            if elem.tag == 'marquee':
                height = elem.get('height')
                width = elem.get('width')
                scrollamount = elem.get('scrollamount')
                if height is not None and width is not None and scrollamount is not None:
                    if height.isdigit() and width.isdigit() and scrollamount.isdigit() \
                        and 0 < float(height) <= settings.getfloat('HEIGHT_MAX') \
                            and 0 < float(width) <= settings.getfloat('WIDTH_MAX') \
                            and float(scrollamount) >= settings.getfloat('SCROLLAMOUNT_MIN'):
                        return True
        return False

    '''
    描述： 检测display是否为none，visibility是否为hidden
    '''

    def is_visible_hidden(self, element):
        visString = None
        whichElem = None
        # 1. 获取自身的display或者visibility属性,如过不存在或者是存在但不为none或者hidden，则继续从父结点中查找
        temp = self.htmlParser.get_element_style_attr_value(element, 'display')
        visible = temp if temp is not None \
            else self.htmlParser.get_element_style_attr_value(element, 'visibility')
        if visible is None or (visible.lower() != 'none' and visible.lower() != 'hidden'):
            parent = self.htmlParser.get_all_parent_element(element)
            for elem in parent:
                temp = self.htmlParser.get_element_style_attr_value(elem, 'display')
                visible = temp if temp is not None \
                    else self.htmlParser.get_element_style_attr_value(elem, 'visibility')
                if visible is not None and (visible.lower() == 'none' or visible.lower() == 'hidden'):
                    visString = visible
                    whichElem = elem
                    break
        else:
            visString = visible
            whichElem = element
        if visString is not None:
            # 2. 找到该属性为none或者为hidden的元素了，判断其是否有id属性
            if 'id' in whichElem.keys():
                # 存在的话则在他的父结点中查找是否存在onmouseover和onmouseout属性,看其中的id是否相同
                idStr = whichElem.get('id')
                parent = self.htmlParser.get_all_parent_element(whichElem)
                for elem in parent:
                    keys = elem.keys()
                    # 当父结点中存在onmouseover和onmouseout时候，获取这两个字符串，并且提取其（ID）！！！思考，若是存在多句getElementById怎么办
                    if 'onmouseover' in keys and 'onmouseout' in keys:
                        matchOver = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onmouseover'),
                                              re.IGNORECASE)
                        matchOut = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onmouseout'),
                                             re.IGNORECASE)
                        if matchOver is not None and idStr in matchOver.group(1):
                            return False
                        elif matchOut is not None and idStr in matchOut.group(1):
                            return False
                        else:
                            # 判断是否为javascript代码在<script>标签下的情况
                            # 此时onmouseover和onmouseout标签下的内容仅仅是要调用的函数时候，说明其代码在javascirpt中，先提取函数名字
                            overFunName = re.search(r'(\w+)\(\)', elem.get('onmouseover'), re.IGNORECASE)
                            outFunName = re.search(r'(\w+)\(\)', elem.get('onmouseout'), re.IGNORECASE)
                            # 如果成功提取函数名，则调用函数查找，函数get_id_in_javascript可以获得当前函数名下所有的ID
                            if overFunName:
                                matchOverList = self.htmlParser.get_id_in_javascript(overFunName.group(1))
                                if len(matchOverList) and idStr in matchOverList:
                                    return False
                            if outFunName:
                                matchOutList = self.htmlParser.get_id_in_javascript(outFunName.group(1))
                                if len(matchOutList) and idStr in matchOutList:
                                    return False
                            continue
                    # 如果该结点中不存在onmouseover和onmouseout， 则查找是否存在onclick
                    elif 'onclick' in keys:
                        matchClick = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onclick'),
                                              re.IGNORECASE)
                        if matchClick is not None and idStr in matchClick.group(1):
                            return False
                        else:
                            # 判断是否为javascript代码在<script>标签下的情况
                            clickFunName = re.search(r'(\w+)\(\)', elem.get('onclick'), re.IGNORECASE)
                            matchClickList = self.htmlParser.get_id_in_javascript(clickFunName.group(1))
                            if len(matchClickList) and idStr in matchClickList:
                                    return False
                            continue
                    else:
                        continue
                # 在他的兄弟结点，以及兄弟结点的子结点中查找是否存在onmouseover和onmouseout属性
                brother = self.htmlParser.get_all_brother_element(whichElem, False)
                brotherBranch = []
                for elem in brother:
                    brotherBranch.extend(self.htmlParser.get_all_child_element(elem))
                for elem in brotherBranch:
                    keys = elem.keys()
                    if 'onmouseover' in keys and 'onmouseout' in keys:
                        matchOver = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onmouseover'),
                                              re.IGNORECASE)
                        matchOut = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onmouseout'),
                                             re.IGNORECASE)
                        if matchOver is not None and idStr in matchOver.group(1):
                            return False
                        elif matchOut is not None and idStr in matchOut.group(1):
                            return False
                        else:
                            # 判断是否为javascript代码在<script>标签下的情况
                            overFunName = re.search(r'(\w+)\(\)', elem.get('onmouseover'), re.IGNORECASE)
                            outFunName = re.search(r'(\w+)\(\)', elem.get('onmouseout'), re.IGNORECASE)
                            if overFunName:
                                matchOverList = self.htmlParser.get_id_in_javascript(overFunName.group(1))
                                if len(matchOverList) and idStr in matchOverList:
                                    return False
                            if outFunName:
                                matchOutList = self.htmlParser.get_id_in_javascript(outFunName.group(1))
                                if len(matchOutList) and idStr in matchOutList:
                                    return False
                            if matchOut is not None or matchOver is not None:
                                # print matchOver.group(1) + ':' + matchOut.group(1)
                                return True
                            else:
                                continue
                    elif 'onclick' in keys:
                        matchClick = re.search(r'getElementById\([\'\"](.*)[\'\"]\)', elem.get('onclick'),
                                              re.IGNORECASE)
                        if matchClick is not None and idStr in matchClick.group(1):
                            return False
                        else:
                            # 判断是否为javascript代码在<script>标签下的情况
                            clickFunName = re.search(r'(\w+)\(\)', elem.get('onclick'), re.IGNORECASE)
                            if clickFunName is not None:
                                matchClickList = self.htmlParser.get_id_in_javascript(clickFunName.group(1))
                                if len(matchClickList) and idStr in matchClick:
                                    return False
                            continue
                    else:
                        continue
                return True
            else:
                # 不存在说明没有属性能改变其是否可见
                return True
        else:
            return False

    '''
    描述： 检测overflow是为hidden时候，width设置小于阈值
    '''

    def is_overflow_width_hidden(self, element):
        overString = None
        widthSize = None
        # 1.获取父类中的overflow、width值
        parent = self.htmlParser.get_all_parent_element(element)
        for elem in parent:
            overflow = self.htmlParser.get_element_style_attr_value(elem, 'overflow')
            width = self.htmlParser.get_element_style_attr_value(elem, 'width')
            if overflow is not None and width is not None:
                overString = overflow
                widthSize = width
                break
        if overString is not None and widthSize is not None:
            if overString.lower() == 'hidden':
                matchNormal = re.search(r'([-]?\d+)\s*(\D+)', widthSize, re.IGNORECASE)
                matchChange = re.search(r'expression_r\(((\d+-)?\d+)\)', widthSize, re.IGNORECASE)
                if matchChange is not None:
                    if eval(matchChange.group(1)) <= settings.getfloat('OVER_WIDTH'):
                        return True
                    else:
                        return False
                elif matchNormal is not None:
                    if matchNormal.group(2).lower() == 'px' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('OVER_WIDTH'):
                        return True
                    elif matchNormal.group(2).lower() == 'em' \
                            and matchNormal.group(1).isdigit() \
                            and (float(matchNormal.group(1)) * 10) <= settings.getfloat('OVER_WIDTH'):
                        return True
                    else:
                        return False
                else:
                    return False
        return False

    '''
    描述： 检测overflow是为hidden时候，height设置小于阈值
    '''

    def is_overflow_height_hidden(self, element):
        overString = None
        heightSize = None
        # 1.获取父类中的overflow、height值
        parent = self.htmlParser.get_all_parent_element(element)
        for elem in parent:
            overflow = self.htmlParser.get_element_style_attr_value(elem, 'overflow')
            height = self.htmlParser.get_element_style_attr_value(elem, 'height')
            if overflow is not None and height is not None:
                overString = overflow
                heightSize = height
                break
        if overString is not None and heightSize is not None:
            if overString.lower() == 'hidden':
                matchNormal = re.search(r'([-]?\d+)\s*(\D+)', heightSize, re.IGNORECASE)
                matchChange = re.search(r'expression_r\(((\d+-)?\d+)\)', heightSize, re.IGNORECASE)
                if matchChange is not None:
                    if eval(matchChange.group(1)) <= settings.getfloat('OVER_HEIGHT'):
                        return True
                    else:
                        return False
                elif matchNormal is not None:
                    if matchNormal.group(2).lower() == 'px' \
                            and matchNormal.group(1).isdigit() \
                            and float(matchNormal.group(1)) <= settings.getfloat('OVER_HEIGHT'):
                        return True
                    elif matchNormal.group(2).lower() == 'em' \
                            and matchNormal.group(1).isdigit() \
                            and (float(matchNormal.group(1)) * 10) <= settings.getfloat('OVER_HEIGHT'):
                        return True
                    else:
                        return False
                else:
                    return False
        return False
