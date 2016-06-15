# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

# FT中文网
@parser
class FTChinesePageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url, byte_data):
        if 'ftchinese.com' in url:
            return True
        else:
            return False

    @staticmethod
    def get_local_processor():
        return 'null'

    def __init__(self):
        super().__init__()
        self.encoding = 'utf-8'

    def get_page_num(self):
        '''页号'''
        
        # 没有页码区
        re = r'<div class="pagination">'
        p = red.re_dict(re, red.S)
        m = p.search(self.html)
        if not m:
            return 1
        
        # 不是第1页
        re = (r'<div class="pagination">'
              r'<span class="current">1</span>'
              )
        p = red.re_dict(re, red.DOTALL)

        m = p.search(self.html)
        if not m:
            return 2
        
        #print('pg_num:', m.group(1))

        return 1

    def get_title(self):
        '''标题'''
        re = r'<h1 class="story-headline">\s*(.*?)\s*</h1>'
        p = red.re_dict(re, red.S)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        s = 'FT中文网'

        return s

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''

        r = (r'<div class="pagination-container">.*?'
             r'<a href="([^"]+)">余下全文</a>'
             )
        p = red.re_dict(r, red.S)
        m = p.search(self.html)

        if not m:
            return ''

        ret = 'http://www.ftchinese.com' + m.group(1)
        
        #print('next_pg_url:', ret)
        return ret

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text):
            '''子函数，返回处理后的文本'''
            
            # 去<script>
            p = red.re_dict(r'<script.*?/script>', red.I|red.A)
            text = p.sub('', text)

            # 去标签
            p = red.re_dict(r'(?!<br\s*/?>|</p>)<[^>]+>', red.I|red.A)
            text = p.sub('', text)
            
            # 换行、行首空格
            p = red.re_dict(r'(?:\x0D\x0A?|<br\s*/?>|</p>)\s*', red.I|red.A)
            text = p.sub(r'\n', text)
            
            # 去html转义
            text = self.de_html_char(text)

            # 三个以上换行
            p = red.re_dict(r'\n+')
            text = p.sub('\n\n', text)

            # 首尾空白
            text = text.strip()

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        replys = list()

        # 回复
        re = r'<div class="story-body">(.*?)<div class="clearfloat">'

        p = red.re_dict(re, red.DOTALL)
        m = p.search(self.html)
        
        item = Reply(self.wrap_get_louzhu(),
                      datetime.now(),
                      process_text(m.group(1)))
        replys.append(item)

#         for i in replys:
#             print('\n∞∞∞∞∞∞∞∞∞ author:{0} time:{1} ∞∞∞∞∞∞∞∞∞\n{2}'.format(
#                 i.author,
#                 i.time,
#                 i.text)
#             )
#         else:
#             print('-------replys: ', len(replys), '-------')

        return replys
