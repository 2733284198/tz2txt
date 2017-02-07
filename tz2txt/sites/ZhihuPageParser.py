# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

# 知乎


@parser
class ZhihuPageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url):
        if 'zhihu.com' in url:
            return True
        else:
            return False

    @staticmethod
    def get_local_processor():
        return 'null'

    def __init__(self):
        super().__init__()
        self.encoding = 'utf-8'
        
    def pre_process_url(self, url):
        p = r'(https://www.zhihu.com/question/\d+)/answer/\d+'
        r = red.re_dict(p, red.I|red.A)
        m = r.search(url)
        if m:
            return m.group(1)
        else:
            return url

    def get_page_num(self):
        '''页号'''
        return 1

    def get_title(self):
        '''标题'''
        re = r'<span class="zm-editable-content">(.*?)</span>'
        p = red.re_dict(re, red.S)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        s = '知乎用户'

        return s

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''

        return ''

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text, username, vote):
            '''子函数，返回处理后的文本'''

            # 去<script>
            p = red.re_dict(r'<script.*?/script>', red.I | red.A)
            text = p.sub('', text)

            # 去标签
            p = red.re_dict(r'(?!<br\s*/?>|</p>)<[^>]+>', red.I | red.A)
            text = p.sub('', text)

            # 换行、行首空格
            p = red.re_dict(r'\x0D\x0A?', red.I | red.A)
            text = p.sub(r'', text)

            p = red.re_dict(r'(?:<br\s*/?>|</p>)\s*', red.I | red.A)
            text = p.sub(r'\n', text)

            # 去html转义
            text = self.de_html_char(text)

            # 三个以上换行
            p = red.re_dict(r'\n+')
            text = p.sub('\n\n', text)

            # 首尾空白
            text = text.strip()

            # 用户名，赞同数
            s = '【知乎用户 %s ，%s人赞同】\n' % (username, vote)
            text = s + text

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = lambda s: datetime.strptime(s, '%Y-%m-%d')
        replys = list()

        # 第1楼

        regex1 = (
            r'<span class="voters text">.*?'
            r'>(\d+)</span>&nbsp;人赞同.*?'
            r'<div class="zm-item-rich-text expandable js-collapse-body"'
            r'.*?data-author-name="([^"]+)".*?'
            r'<div class="zm-editable-content clearfix">'
            r'(.*?)'
            r'</div>\s*</div>\s*<a class="zg-anchor-hidden ac".*?'
            r'>(?:发布于|编辑于)\s*([\d-]+)</a>'
        )
        p = red.re_dict(regex1, red.DOTALL)
        miter = p.finditer(self.html)

        d1 = ((m.group(1), m.group(2), m.group(3), m.group(4)) for m in miter)
        d2 = (('知乎用户', dt(date), process_text(text, user, vote))
              for vote, user, text, date in d1)
        d3 = (Reply(x, y, z) for x, y, z in d2)
        replys.extend(d3)

        return replys
