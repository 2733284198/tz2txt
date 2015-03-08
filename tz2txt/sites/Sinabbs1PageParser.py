# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

class Sinabbs1PageParser(AbPageParser):
    '''示例页面解析器'''

    @staticmethod
    def should_me(url, byte_data):
        if 'sina.com.cn' in url and 'thread' in url:
            return True
        else:
            return False

    @staticmethod
    def get_local_processor():
        return 'sinabbs1'

    def __init__(self):
        super().__init__()
        self.encoding = 'gb18030'

    def get_page_num(self):
        '''页号'''
        r = (r'<div class="pages">'
             r'.*?'
             r'<strong>(\d+)</strong>'
             r'.*?</div>'
            )
        p = red.re_dict(r, red.DOTALL)
        m = p.search(self.html)
        #print('pn:',  m.group(1))

        # 只有一页时，是搜不到的
        if not m:
            return 1
        else:
            return int(m.group(1))

    def get_title(self):
        '''标题'''
        r = (r'<div\s+id="nav">'
             r'.*?&raquo;\s*([^<]+)\s*</div>'
            )
        p = red.re_dict(r, red.S)

        m = p.search(self.html)
        #print('title:', m.group(1).strip())

        return m.group(1).strip()

    def get_louzhu(self):
        '''楼主'''
        return ''

    def get_next_pg_url(self):
        '''下一页url'''
        r = r'<a\s+href="([^"]+)"\s+class="next">\&rsaquo;\&rsaquo;</a>'
        p = red.re_dict(r)
        m = p.search(self.html)

        if not m:
            return ''

        path = m.group(1).replace('&amp;', '&')
        ret = self.get_hostname() + r'/' + path
        #print('next_pg_url:', ret)
        return ret

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text):
            '''子函数，返回处理后的文本'''

            # ‘该帖被浏览  5,183 次，回复 96 次’
            r = r'<span\s+.*>该帖被浏览.*?次，回复.*?次 </span>'
            p = red.re_dict(r)
            text = p.sub(r'', text)

            # 替换图片
            regex = (r'<img\s+[^>]*?src\s*=\s*'
                     r'"([^"]+)"[^>]*?onmouseout="attachimginfo\(this'
                     r'[^>]*>'
                     )
            p = red.re_dict(regex, red.IGNORECASE)
            text = p.sub(r'\n[img]\1[/img]', text)

            # 图片下面的日期
            regex = (r'<div\s+class="t_smallfont">'
                     r'\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}'
                     r'<br\s*/?></div>'
                     )
            p = red.re_dict(regex, red.IGNORECASE)
            text = p.sub(r'', text)

            # 引用
            r = (r'<div\s+class="quote">'
                 r'.*?<blockquote>原帖由\s*<i>(.*?)(?:\(login\))?</i>'
                 r'.*?</a>(?:<br\s*/?>|\s)*'
                 r'(.*?)(?:<br\s*/?>|\s)*'
                 r'</blockquote></div>'
                 )
            p = red.re_dict(r, red.I|red.S)
            text = p.sub(r'\n回复 \1:\n【引用开始】\2\n【引用结束】\n', text)

            # 去标签
            p = red.re_dict(r'(?!<br\s*/?>|</p>)<[^>]+>', red.I)
            text = p.sub('', text)

            # 去html转义
            text = self.de_html_char(text)
            
            # 换行、行首空格
            p = red.re_dict(r'(?:\x0D\x0A?|<br\s*/?>|</p>)\s*', red.I)
            text = p.sub(r'\n', text)

            # 三个以上换行
            p = red.re_dict(r'\n{3,}')
            text = p.sub('\n\n', text)

            # 首尾空白
            text = text.strip()

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = lambda s:datetime.strptime(s, '%Y-%m-%d %H:%M')
        replys = list()

        # 楼层
        regex = (
            r'<div\s+class="myInfo_up">(?!\s*该用户被屏蔽)'
            r'.*?'
            r'<a.*?class="f14">(.*?)</a>'
            r'.*?'
            r'>发表于：(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})</font>'
            r'.*?'
            r'<div\s+class="mybbs_cont"\s*>\s*(.*?)\s*</div>'
            r'\s+(?:<fieldset>|<div class="myInfo">'
            r'|<div\s+id="post_rate_div_\d+">)'
            )
        p = red.re_dict(regex, red.DOTALL)
        miter = p.finditer(self.html)

        d1 = ( (m.group(1), m.group(2), m.group(3)) for m in miter)
        d2 = ( (x, dt(y), process_text(z)) for x,y,z in d1)           
        d3 = ( Reply(x, y, z) for x,y,z in d2)
        replys.extend(d3)

##        for i in replys:
##            print('\n∞∞∞∞∞∞∞∞∞ author:{0} time:{1} ∞∞∞∞∞∞∞∞∞\n{2}'.format(
##                                                        i.author,
##                                                        i.time,
##                                                        i.text)
##                    )
##        else:
##            print('-------replys: ', len(replys), '-------')
            
        return replys

# 注册此页面解析器，参数为页面解析器的类名
AbPageParser.register_me(Sinabbs1PageParser)

#别忘了把此文件写进__init__.py里
