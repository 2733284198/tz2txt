# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

# 中国社会科学网
@parser
class cssnPageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url, byte_data):
        if 'cssn.cn' in url:
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
        re = r'var currentPage = (\d+);//所在页从0开始'
        p = red.re_dict(re, red.DOTALL)

        m = p.search(self.html)
        if not m:
            return 1
        
        #print('pg_num:', m.group(1))

        return int(m.group(1)) + 1

    def get_title(self):
        '''标题'''
        re = r'<span class="TitleFont">(.*?)</span>'
        p = red.re_dict(re)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        s = '中国社会科学网'

        return s

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''
        
        r = r'''//createPageHTML\((\d+), (\d+), "'''
        p = red.re_dict(r, red.DOTALL)
        m = p.search(self.html)
        
        if not m:
            return ''
        
        # 判断最后一页
        all = int(m.group(1))
        current = int(m.group(2))+1
        if current == all:
            return ''
        
        # 是首页
        if self.wrap_get_page_num() == 1:
            return self.url.replace('.shtml', '_1.shtml')

        # 其它情况
        idx = self.url.rfind('_')
        ret = self.url[:idx+1] + str(current) + '.shtml'
        #print('next_pg_url:', ret)
        return ret

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text):
            '''子函数，返回处理后的文本'''
            
            # 去style
            p = red.re_dict(r'<style.*?</style>', red.I|red.S|red.A)
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
            p = red.re_dict(r'\n{3,}')
            text = p.sub('\n\n', text)
            
            # 去注解编号
            p = red.re_dict(r'\(\d+\)')
            text = p.sub('', text)

            # 首尾空白
            text = text.strip()

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = lambda s: datetime.strptime(s, '%Y-%m-%d')
        replys = list()

        # 日期
        r = r'<meta name="publishdate" content="(.*?)">'
        p = red.re_dict(r)
        m = p.search(self.html)
        date_str = m.group(1)

        # 回复
        re = (r'(?:<div id="bigtitle">|'
              r'<div class="?TRS_Editor"?>)(.*?)<script>')

        p = red.re_dict(re, red.DOTALL)
        m = p.search(self.html)
        
        item = Reply(self.wrap_get_louzhu(),
                      dt(date_str),
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
