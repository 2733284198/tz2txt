# coding=utf-8
import html
import re
from enum import IntEnum
from datetime import datetime

from tzdatastruct import *
from AbPageParser import *

class STRICT(IntEnum):
    NO = 0
    ONE = 1
    HAS = 2
    TWOM = 3
    
# 处理用的正则式list
# 三个元素分别为：匹配正则，flags，替换
sample_re_list = (
            # 示例
            [
                r'',
                0,
                r'',
                STRICT.NO
            ],
            )

def do_replace(text, re_list):
    '''用re_list进行替换处理'''
    print('>用正则式列表替换')
    
    # 编译
    for i in re_list:
        i.append(re.compile(''.join(i[0]), i[1]))
        #print(''.join(i[0]))

    process_count = 0
    for r in re_list:
        text, n = r[4].subn(r[2], text)
        
        # 检查约束
        if r[3] == STRICT.ONE and n != 1:
            raise Exception('约束错误：', r[0])
        elif r[3] == STRICT.HAS and n < 1:
            raise Exception('约束错误：', r[0])
        elif r[3] == STRICT.TWOM and n <= 1:
            raise Exception('约束错误：', r[0])
        
        if n > 0:
            process_count += 1 

    print('...共%d个正则，做了%d次替换' % (len(re_list), process_count))
    return text

re_list = (
           # 总提取
            [
                (r'^.*?'
                 r'<div class="lemma-summary".*?>'
                 r'(.*?)'
                 r'(?:<div class="open-tag-title">|'
                 r'<div class="album-list">|'
                 r'<(?:dt|ul) class="reference-(?:title|list)">)'
                 r'.*$'
                 ),
                re.S|re.I,
                r'\1',
                STRICT.ONE
            ],
           
           # 去掉 基本信息
            [
                (r'^(.*?)<div class="basic-info.*?>',
                 r'.*?<div class="lemma-catalog">'
                 ),
                re.S,
                r'\1',
                STRICT.NO
            ],
           
            # 去掉 目录
            [
                (r'^(.*?)<h2 class="block-title">目录</h2>',
                 r'.*</ol>\s*</div>\s*</div>\s*</div>'
                 ),
                re.S,
                r'\1',
                STRICT.ONE
            ],
           
            # 去掉 热点关注
            [
                (r'<ul class="focusAndRelation">',
                 r'.*?</ul>'
                 ),
                re.S,
                r'',
                STRICT.NO
            ],
           
            # 去掉 编辑
            [
                r'>编辑</a>',
                0,
                r'></a>',
                STRICT.NO
            ],
           
            # 主词条
            [
                r'<span>主词条: </span>.*?</div>',
                re.S,
                r'',
                STRICT.NO
            ],     
           
           # table
            [
                r'<table log-set-param="table_view".*?</table>',
                re.S,
                r'[省略一张表格]\n',
                STRICT.NO
            ],
           
            # 图片下注释
            [
                r'<(?:span|div) class="description">.*?</(?:span|div)>',
                re.S,
                r'',
                STRICT.NO
            ],
           
            # 图片
            [
                r'<div class="lemma-picture.*?</div>',
                re.S,
                r'',
                STRICT.NO
            ],  
           
            # 引用脚标
            [
                (r'<sup>\[[\d-]+\]</sup><a class="sup-anchor" '
                 r'name="[^"]*">&nbsp;</a>\s*'),
                re.S,
                r'',
                STRICT.NO
            ],
            
            # 小标题前缀
            [
                (r'<span class="title-prefix">(.*?)</span>'),
                0,
                r'小标题：',
                STRICT.NO
            ],

            # 点号
            [
                (r'<li'),
                re.S,
                r'·<li',
                STRICT.NO
            ], 
            
            # TA说
            [
                (r'<div id="hotspotmining_s".*?'
                 r'</div>\s*</div>\s*</div>'),
                re.S,
                r'',
                STRICT.NO
            ],
            
            # 城市百科
            [
                (r'<div class="city-guide.*?</div>'),
                re.S,
                r'',
                STRICT.NO
            ],
           
            # javascript
            [
                r'<script.*?</script>',
                re.S,
                r'',
                STRICT.NO
            ],            

            # style
            [
                r'<style.*?</style>',
                re.S,
                r'',
                STRICT.NO
            ],                
           
           #===================================
           
           # html标签
            [
                r'''<(?:[^"'>]|"[^"]*"|'[^']*')*>''',
                0,
                r'',
                STRICT.NO
            ],
           
            # 注释，ie:[12]
            [
                r'\[[\d-]*\]',
                0,
                r'',
                STRICT.NO
            ],
           
            # CR,\r
            [
                r'\x0D+',
                0,
                '',
                STRICT.NO
            ],
           
            # 大量空格变两个
            [
                r' {3,}',
                0,
                r'  ',
                STRICT.NO
            ],
           
            # 大量换行变两个
            [
                r'\n{3,}',
                0,
                r'\n\n',
                STRICT.NO
            ],
            )

# 百度百科
@parser
class BaiduBaikePageParser(AbPageParser):

    '''示例页面解析器'''

    @staticmethod
    def should_me(url):
        if 'baike.baidu.com' in url:
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
        return 1

    def get_title(self):
        '''标题'''
        re = r'<title>(.*?)_百度百科</title>'
        p = red.re_dict(re, red.S)

        m = p.search(self.html)
        #print('title:', m.group(1))

        return m.group(1)

    def get_louzhu(self):
        '''楼主'''
        s = '百度百科'

        return s

    def get_next_pg_url(self):
        '''下一页url，末页则返回空字符串'''
        return ''

    def get_replys(self):
        '''返回Reply列表'''
        
        # 处理
        string = do_replace(self.html, re_list)
        
        string = html.unescape(string)
    
        string = string.replace('•', '·')      # gbk对第一个圆点不支持
        string = string.replace('\xA0', ' ')   # 不间断空格
        string = string.replace('\u3000', ' ') # 中文(全角)空格

        string = string.strip()
        
        # 返回列表
        item = Reply(self.wrap_get_louzhu(),
              datetime.now(),
              string)

        return [item]
