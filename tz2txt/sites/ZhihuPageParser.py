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

        def process_text(text, username=None, vote=None):
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
            if username is not None:
                s = '【知乎用户 %s ，%s人赞同】\n' % (username, vote)
                text = s + text + '\n'

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = datetime.now()
        replys = list()
        zhihuuser = '知乎用户'

        # 原题
        p = (r'<div id="zh-question-detail".*?'
             r'<div class="zm-editable-content">'
             r'(.*?)'
             r'</div>\s*</div>\s*<div'
            )
        r = red.re_dict(p, red.DOTALL)
        m = r.search(self.html)
        rpl = Reply(zhihuuser,
                    dt,
                    process_text(m.group(1))
                    )
        replys.append(rpl)

        # 回复
        regex1 = (
            r'<span class="voters text">.*?'
            r'>(\d+)</span>&nbsp;人赞同.*?'
            r'<div class="zm-item-rich-text expandable js-collapse-body"'
            r'.*?data-author-name="([^"]+)".*?'
            r'<div class="zm-editable-content clearfix">'
            r'(.*?)'
            r'</div>\s*</div>\s*<a class="zg-anchor-hidden ac"'
        )
        p = red.re_dict(regex1, red.DOTALL)
        miter = p.finditer(self.html)

        d1 = ((m.group(1), m.group(2), m.group(3)) for m in miter)
        d2 = ((zhihuuser, dt, process_text(text, user, vote))
              for vote, user, text in d1)
        d3 = (Reply(x, y, z) for x, y, z in d2)
        replys.extend(d3)

        return replys
