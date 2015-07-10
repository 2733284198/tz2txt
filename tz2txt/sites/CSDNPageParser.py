# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

@parser()
class CSDNPageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url, byte_data):
        if 'csdn.net' in url:
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
        re = (r'<div class="page_nav">.*?'
             r'<li class="select".*?'
             r'>(\d+)</a>')
        p = red.re_dict(re, red.DOTALL)

        m = p.search(self.html)
        #print('pg_num:', m.group(1))

        return int(m.group(1))

    def get_title(self):
        '''标题'''
        re = r'<span class="title.*?">(.*?)</span>\s*<span>'
        p = red.re_dict(re)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        p = red.re_dict(r' <a class="p-author".*?>(.*?)</a>')

        m = p.search(self.html)
        #print('lz:', m.group(1))

        return m.group(1)

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''
        r = (r'<div class="page_nav">.*?'
             r'<a href="([^"]+)" class="next">下一页</a>')
        p = red.re_dict(r, red.DOTALL)
        m = p.search(self.html)

        if not m:
            return ''

        ret = self.get_hostname() + m.group(1)
        #print('next_pg_url:', ret)
        return ret

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text):
            '''子函数，返回处理后的文本'''

            # 引用
            re = (r'.*<fieldset>.*?楼&nbsp;(.*?)&nbsp;的回复.*?'
                  r'<blockquote>(.*?)</fieldset>\s*(.*?)\s*$')
            p = red.re_dict(re, red.DOTALL)
            text = p.sub(r'回复 \1：\n【引用开始】\2\n【引用结束】\3', text)

            # 去标签
            p = red.re_dict(r'(?!<br\s*/?>|</p>)<[^>]+>', red.I)
            text = p.sub('', text)

            # 换行、行首空格
            p = red.re_dict(r'(?:\x0D\x0A?|<br\s*/?>|</p>)\s*', red.I)
            text = p.sub(r'\n', text)
            
            # 去html转义
            text = self.de_html_char(text)
            
            # 本帖最后由 .. 于 .. 编辑
            re = (r'本帖最后由 .{1,50}? 于 [-\d\s]+ 编辑')
            p = red.re_dict(re)
            text = p.sub('', text)

            # 三个以上换行
            p = red.re_dict(r'\n{3,}')
            text = p.sub('\n\n', text)

            # 首尾空白
            text = text.strip()

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        replys = list()

        re = (
            r'class="post_info.*?" data-username="(.*?)".*?'
            r'<span class="time">.*?于：(.*?)</span>.*?'
            r'<div class="post_body">(.*?)'
            r'''(?:<div id='topic-extra-info'>|</td>)'''
        )

        p = red.re_dict(re, red.DOTALL)
        retlst = p.finditer(self.html)
        
        d1 = ((m.group(1), m.group(2).strip(), m.group(3)) for m in retlst)
        d2 = ((x, dt(y), process_text(z)) for x, y, z in d1)
        d3 = (Reply(x, y, z) for x, y, z in d2)
        replys.extend(d3)

#         for i in replys:
#             print('\n∞∞∞∞∞∞∞∞∞ author:{0} time:{1} ∞∞∞∞∞∞∞∞∞\n{2}'.format(
#                 i.author,
#                 i.time,
#                 i.text)
#             )
#         else:
#             print('-------replys: ', len(replys), '-------')

        return replys
