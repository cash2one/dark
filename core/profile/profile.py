# -*- coding: utf-8 -*-
'''
profile.py

Author: peta
Date: 20150805

定义处理配置文件的类。
'''
import codecs
import ConfigParser
import os
import shutil

from core.settings.settings import settings
from core.exception.DarkException import DarkException
from core.directory.homeDir import get_home_dir, create_home_dir
from core.directory.localDir import get_local_dir
from i18n import _

class Profile:
    '''
    Profile类定义操作配置文件的方法。
    '''

    def __init__(self, profname='', workdir=None):
        '''
        构造函数。

        @:parameter profname: 文件名（可带路径）。
        @:parameter workdir: 工作目录名。
        '''
        create_home_dir()
        # 默认的optionxform把option转换为小写，我们需要保持原样。
        optionxform = lambda opt: opt
        self._config = ConfigParser.ConfigParser()
        self._config.optionxform = optionxform
        
        if profname:
            profname = self._getRealProfileName(profname, workdir)
            with codecs.open(profname, "rb", settings.get('DEFAULT_ENCODING')) as fp:
                try:
                    self._config.readfp(fp)
                except ConfigParser.Error, cpe:
                    raise DarkException, _('ConfigParser error in profile: "(profname)%s". Exception: "(exception)%s"') % \
                            {'profname':profname, 'exception':str(cpe)}
                except Exception, e:
                    raise DarkException, _('Unknown error in profile: "(profname)%s". Exception: "%(exception)s"') % \
                            {'profname': profname, 'exception':str(e)}

        self._profileFileName = profname
    
    def _getRealProfileName(self, profilename, workdir):
        '''
        返回profilename的绝对路径。

        @:parameter profilename: 文件名（可带路径）。
        @:parameter workdir: 工作目录名。
        @return: profile文件的绝对限定名称。
        @raise darkException: 如果没有profile被发现，抛出一个带有恰当描述消息的异常。
        '''
        # 别名
        ospath = os.path
        
        # 如果需要，添加后缀
        if not profilename.endswith('.dark'):
            profilename += '.dark'
        profname = profilename
        
        # 试着去发现文件
        found = ospath.isfile(profname)
        
        if not (ospath.isabs(profname) or found):
            profname = ospath.join(get_home_dir(), 'profiles', profilename)
            found = ospath.isfile(profname)
            # 在指定的目录下查找
            if not found and workdir:
                profname = ospath.join(workdir, profilename)
                found = ospath.isfile(profname)
                        
        if not found:
            raise DarkException, _('The profile "%(profilename)s" wasn\'t found') % {'profilename':profilename}
        return ospath.abspath(profname)

    def getProfileFile(self):
        '''
        返回profile文件的绝对限定名称。

        @return: profile文件的绝对限定名称。
        '''
        return self._profileFileName
    
    def remove(self):
        '''
        删除创建该profile实例的profile文件。

        @return: 成功返回True。
        @raise darkException: 如果没有删除成功，抛出异常。
        '''
        try:
            os.unlink(self._profileFileName)
        except Exception, e:
            raise DarkException, _('An exception occurred while removing the profile. Exception: %(exception)s') % {'exception':str(e)}
        else:
            return True
            
    def copy(self, copyProfileName):
        '''
        拷贝profile配置文件的一个副本到copyProfileName。

        @:parameter copyProfileName: 目标拷贝文件名(可以带路径)。
        @return: 成功拷贝，返回True。
        @raise darkException: 拷贝失败，抛出异常。
        '''
        newProfilePathAndName = copyProfileName
        
        # 检查是否带路径
        if os.path.sep not in copyProfileName:
            dir = os.path.dirname(self._profileFileName)
            newProfilePathAndName = os.path.join(dir, copyProfileName)
        
        # 检查后缀名是否是.dark
        if not newProfilePathAndName.endswith('.dark'):
            newProfilePathAndName += '.dark'
        
        try:
            shutil.copyfile(self._profileFileName, newProfilePathAndName)
        except Exception, e:
            raise DarkException, _('An exception occurred while copying the profile. Exception: %(exception)s') + {'exception':str(e)}
        else:
            # 现在必须修改拷贝后的profile文件
            pNew = Profile(newProfilePathAndName)
            pNew.setName(copyProfileName)
            pNew.save(newProfilePathAndName)
            
            return True
            
    def save(self, file_name=''):
        '''
        保存修改到配置文件。
        
        @:parameter file_name: 配置文件名(可带路径)，默认为空。
        '''
        if not self._profileFileName:
            if not file_name:
                raise DarkException, _('Error while saving profile, you didn\'t specified the file name')
            else: 
                # 用户指定的文件
                if not file_name.endswith('.dark'):
                    file_name += '.dark'
                
            if os.path.sep not in file_name:
                file_name = os.path.join(get_home_dir(), 'profiles', file_name)
            self._profileFileName = file_name
            
        try:
            fileHandler = open(self._profileFileName, 'w')
        except:
            raise DarkException, _('Failed to open profile file: %(profileFileName)s') % {'profileFileName': self._profileFileName}
        else:
            self._config.write(fileHandler)

    def getPlugins(self, pluginType):
        '''
        获取启用的插件列表。
        '''
        res = []
        for section in self._config.sections():
            try:
                type, name = section.split('.')
            except:
                pass
            else:
                if type == pluginType:
                    res.append(name)
        return res

    def getOptions(self, section, configuraleInstance):
        '''
        获取配置节点选项。

        @:parameter section: 配置节点（区域）名称。
        @:parameter configuraleInstance: 可配置实例对象。
        @return: OptionList对象。
        '''
        optionList = configuraleInstance.getOptions()
        for option in self._config.options(section):
            try:
                value = self._config.get(section, option)
            except KeyError:
                # 我们应该确保永远不会运行到此
                raise DarkException, _('The option "%(option)s" is unknown for the "%(section)s" section') % {'option':option, 'section':section}
            else:
                optionList[option].value = value # 设置option对象value属性。

    def getDbType(self):
        '''
        获取数据库类型。
        '''
        for section in self._config.sections():
            if section == 'db':
                for option in self._config.options(section):
                    if option == 'type':
                        return self._config.get(section, option)

        return None

    def getDbInfo(self):
        for section in self._config.sections():
            if section == 'db':
                result = []
                for key, value in self._config.items(section):
                    if key != 'type':
                        result.append((key, value))
                return dict(result)

        return None

    def getLogType(self):
        for section in self._config.sections():
            if section == 'log':
                for option in self._config.options(section):
                    if option == 'isTextPlugin':
                        return self._config.get(section, option)

        return None


    def getProfileValue(self, sectionName, optionName, valueType='string'):
        '''
        获取配置文件指定section、option的值。

        @param sectionName: 配置区域名称。
        @param optionName: 配置选项名称。
        @param valueType: 返回值类型，取值‘int’、‘string’、'list’
        '''
        for section in self._config.sections():
            if section == sectionName:
                for option in self._config.options(section):
                    if option == optionName:
                        if valueType == 'string':
                            return self._config.get(section, option)
                        elif valueType == 'int':
                            return self._config.getint(section, option)
                        else:
                            aList = []
                            for value in self._config.get(section, option).split(','):
                                aList.append(value)
                            return aList

        return None


pf = Profile(get_local_dir() + os.path.sep + 'conf.dark')
