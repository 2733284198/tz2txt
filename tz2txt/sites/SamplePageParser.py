# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

@parser
class SamplePageParser(AbPageParser):
    '''示例页面解析器'''

    @staticmethod
    def should_me(url):
        if 'sample.com' in url:
            return True
        else:
            return False

    @staticmethod
    def get_local_processor():
        return 'sample'

    def __init__(self):
        super().__init__()
        self.encoding = 'utf-8'

    def get_page_num(self):
        '''页号'''
        return 1

    def get_title(self):
        '''标题'''
        return 'title'

    def get_louzhu(self):
        '''楼主'''
        return 'louzhu'

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''
        return 'next_url'

    def get_replys(self):
        '''返回Reply列表'''
        return None
