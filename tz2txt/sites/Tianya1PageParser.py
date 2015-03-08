# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

class Tianya1PageParser(AbPageParser):
    '''天涯页面'''

    @staticmethod
    def should_me(url, byte_data):
        if 'tianya.cn' in url:
            return True
        else:
            return False

    @staticmethod
    def get_local_processor():
        return 'Tianya1'

    def __init__(self):
        super().__init__()
        self.encoding = 'utf-8'

    def get_page_num(self):
        '''页号'''
        p = red.re_dict(r'var bbsGlobal = {.*?page : "(\d+)",',
                         red.DOTALL
                         )

        m = p.search(self.html)
        #print('pn:',  m.group(1))

        return int(m.group(1))

    def get_title(self):
        '''标题'''
        r1 = (r'<h1\s+class="atl-title">\s*<span\s+class="s_title">'
              r'(.*?)'
              r'</span>\s*<[^/]'
              )
        p1 = red.re_dict(r1, red.S)
        m = p1.search(self.html)
        temp = m.group(1)

        p2 = red.re_dict(r'<[^>]+>')
        return p2.sub('', temp)

    def get_louzhu(self):
        '''楼主'''
        p = red.re_dict(r'<meta name="author" content="([^"]+)">')

        m = p.search(self.html)
        #print('lz:', m.group(1))

        return m.group(1)

    def get_next_pg_url(self):
        '''下一页url'''
        p = red.re_dict(r'<a href="([^"]+)" class="js-keyboard-next">下页</a>')
        m = p.search(self.html)

        if not m:
            return ''
        
        ret = self.get_hostname() + m.group(1)
        #print('next_pg_url:', ret)
        return ret

    def get_replys(self):
        '''返回Reply列表'''

        def process_text(text, pg_num):
            '''子函数，返回处理后的文本'''
            # utf-8编码0xe38080的空白，变成普通空格
            text = text.replace('　', ' ')
            
            # <br>->\n，去掉行首空格
            p = red.re_dict(r'(?:\n|<br/??>)\s*', red.IGNORECASE)
            text = p.sub(r'\n', text)

            # <p ..></p>
            p = red.re_dict(r'<p[\s>].*?</p>', red.IGNORECASE)
            text = p.sub(r'', text)

            # <table></table>
            p = red.re_dict(r'<table[\s>].*?</table>', red.IGNORECASE)
            text = p.sub(r'', text)

            # 【发自爱天涯Android客户端】
            p = red.re_dict(r'【发自[^\n]{1,20}】')
            text = p.sub(r'', text)

            # [来自UC浏览器]
            p = red.re_dict(r'\[来自[^\n]{1,15}浏览器\]')
            text = p.sub(r'', text)

            # 替换图片
            regex = (r'''<img\s+.*?original\s*=\s*['"]'''
                     r'''(http://[^'"]+)['"].*?(?:/>|</img>|>)'''
                     )
            p = red.re_dict(regex, red.IGNORECASE)
            text = p.sub(r'\n[img '+str(pg_num)+r']\1[/img]', text)

            # 链接
            regex = r'<(?:a|A)\s+[^>]*>(.*?)<[^>]*>'
            p = red.re_dict(regex)
            text = p.sub(r'\1', text)

            # 三个以上换行
            p = red.re_dict(r'\n{3,}')
            text = p.sub(r'\n\n', text)
            
            # 去标签
            text = red.sub(r'''<(?:[^"'>]|"[^"]*"|'[^']*')*>''', r'', text)

            # html字符
            text = self.de_html_char(text)

            # 首尾空白
            text = text.strip()

            return text

        # ----------------------
        # get_replys(self) 开始
        # ----------------------
        dt = lambda s:datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        replys = list()
        pg_num = self.get_page_num()
        
        # 独特的第一页第1楼
        if pg_num == 1:
            regex1 = (
                r'<div class="atl-main">'
                r'.*?'
                r'<div class="bbs-content clearfix">\s*'
                r'(.*?)\s*'
                r'</div>.{0,120}?<div id="alt_action"'
                r'.*?'
                r'_time="(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)" _name="([^"]+)">'
                )
            p = red.re_dict(regex1, red.DOTALL)
            m = p.search(self.html)
            if m:
                rpl = Reply(m.group(3),
                            dt(m.group(2)),
                            process_text(m.group(1), pg_num)
                            )
                replys.append(rpl)
            else:
                raise Exception('无法得到第一页第1楼')

        # 其余楼层
        regex2 = (
            r'<span>(?:作者|<strong class="host">楼主</strong>)：'
            r'<a.*?uname="([^"]+)"'
            r'.*?'
            r'<span>时间：(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)</span>'
            r'.*?'
            r'<div class="bbs-content">(.*?)</div>'
            )
        p = red.re_dict(regex2, red.DOTALL)
        miter = p.finditer(self.html)

        d1 = ( (m.group(1), m.group(2), m.group(3)) for m in miter)
        d2 = ( (x, dt(y), process_text(z, pg_num)) for x,y,z in d1)                
        d3 = ( Reply(x, y, z) for x,y,z in d2)
        replys.extend(d3)

##        for i in replys:
##            print('\n∞∞∞∞∞∞∞∞∞ author:{0} time:{1} ∞∞∞∞∞∞∞∞∞\n{2}'.format(
##                                                      i.author,
##                                                      i.time,
##                                                      i.text)
##                  )
##        else:
##            print('-------replys: ', len(replys), '-------')
            
        return replys


AbPageParser.register_me(Tianya1PageParser)

