# coding=utf-8

from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

@parser
class Tieba1PageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url):
        if 'tieba.baidu.com' in url:
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
        p = red.re_dict(r'PageData\.pager\s*=\s*\{"cur_page":(\d+),')

        m = p.search(self.html)
        #print('pg_num:', m.group(1))

        return int(m.group(1))

    def get_title(self):
        '''标题'''
        re = r'PageData\.thread\s*=.*?title:\s*"(?:回复：)?([^"]+)"'
        p = red.re_dict(re)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        p = red.re_dict(r'PageData\.thread\s*=\s*{\s*author:\s*"([^"]+)"')

        m = p.search(self.html)
        #print('lz:', m.group(1))

        return m.group(1)

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''
        r = r'<a\s+href="([^"]+)">下一页</a>'
        p = red.re_dict(r)
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

            # 替换图片
            regex = (r'<img\s+'
                     r'[^>]*?'
                     r'class="BDE_Image"[^>]*?'
                     r'src\s*=\s*"([^"]+)"[^>]*>'
                     )
            p = red.re_dict(regex, red.IGNORECASE|red.A)
            text = p.sub(r'\n[img]\1[/img]', text)

            # 去掉图片，来自...相册
            regex = (r'<span\s+class="apc_src_wrapper">图片来自：'
                     r'.*?'
                     r'</span>'
                     )
            p = red.re_dict(regex, red.IGNORECASE|red.A)
            text = p.sub(r'', text)
            
            # 去语音
            regex = (r'<div class="voice_player voice_player_pb'
                     r'.*?'
                     r'</div>\s*'
                     )
            p = red.re_dict(regex, red.S)
            text = p.sub(r'【一段语音】\n', text)
            
            # 去标签
            p = red.re_dict(r'(?!<br\s*/?>|</p>)<[^>]+>', red.I|red.A)
            text = p.sub('', text)

            # 去html转义
            text = self.de_html_char(text)

            # 换行、行首空格
            p = red.re_dict(r'(?:\x0D\x0A?|<br\s*/?>|</p>)\s*', red.I|red.A)
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
        dt = lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M')
        replys = list()

        format1 = (
            r'<img\s*username="([^"]+)".*?'
            r'class="d_post_content\s+j_d_post_content\s*".*?>'
            r'(.*?)<div\s+class="user-hide-post.*?'
            r'class="tail-info">(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2})'
        )

        # 提取
        p = red.re_dict(format1, red.DOTALL)
        retlst = p.findall(self.html)
      
        d1 = ((m[0], m[2], m[1]) for m in retlst)   
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
