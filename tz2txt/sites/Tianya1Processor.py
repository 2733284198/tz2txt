# coding=utf-8

import color
from red import red
from BaseProcessor import *

re_line = r'[-—=~～＝_…－＿]'
re_separater = re_line + r'{7,}'
re_longseparater = re_line + r'{16,}'

re_datetime = (r'\b\d{4}-\d{1,2}-\d{1,2}\s+'
               r'\d{1,2}:\d{1,2}(?::\d{1,2}(?:\.\d{0,4})?)?\b')
re_str = (r'(?:'
          r'(?:回复日期|提交日期|发表日期|时间|来自[^\n]{1,20})'
          r'(?:：|:)'
          r')'
          )

@processor
class Tianya1Processor(BaseProcessor):

    # 处理用的正则式list
    # 三个元素分别为：匹配正则，flags，替换
    re_list = (     
                # 第一行是线
                [
                    (r'^\s*', re_separater, r'\s*'),
                    0,
                    r''
                ],
               
                # 整体的最后是线
                [
                    (r'\s*', re_separater, r'\s*$'),
                    0,
                    r''
                ],
               
                # 行首 空白 线 行尾
                [
                    (r'^\s+', re_separater, r'$'),
                    red.M,
                    r'==============='
                ],
               
                # 行首 线 空白 行尾
                [
                    (r'^', re_separater, r'\s+$'),
                    red.M,
                    r'==============='
                ],

                # 一行结尾是长线
                [
                    (r'(?<!\n)(?<!', re_line , r')', 
                     re_longseparater, r'\n'),
                    0,
                    r'\n===============\n'
                ],

                # (行首)线(紧接)一段内容
                [
                    (r'^(?=(', re_separater, r'))'
                     r'\1'
                     r'(\S)'),
                    red.M,
                    r'===============\n\2'
                ],

                # (线\s){2,}
                [
                    (r'(?:', re_separater, r'\s+){2,}'),
                    0,
                    r'\n===============\n'
                ],
               
                # 内容 长线 内容
                [
                    (r'(?<=\S)(?<!', re_line , r')',
                     r'(?=(', re_longseparater, r'))\1', 
                     r'(?=\S)'),
                    0,
                    r'\n===============\n'
                ],

                # 引用作者 --------------------

                # @username (回复日期：)2011-08-28 19:12:45 (回复)
                [
                    (r'@(\S{1,16})\s+', re_str, r'?', re_datetime,
                     r'(?:\s+回复\b)?\s*'),
                    0,
                    r'@@\1##\n'
                ],

                # @username 186楼 (2013-03-08 21:03:36)
                [
                    (r'@(\S{1,16})\s+\d+楼\s+(?:', re_datetime, r')?\s*'),
                    0,
                    r'@@\1##\n'
                ],

                # 作者：username　回复日期：2008-1-2　0:47:20
                [
                    (r'(?:(?:(?:作?者|楼?主)(?:：|:))|^)\s*'
                     r'(\S{1,16})\s+',
                     re_str, r'?\s*', re_datetime, r'(?:\s+回复\b)?\s*'
                     ),
                    red.M,
                    r'@@\1##\n'
                ],

                # 回复第1696楼(作者:@username 于 2014-04-23 20:28)
                [
                    (r'回复第\d+楼\(作者:\s*@(\S{1,16})\s+于\s+',
                     re_datetime, r'\)\s*'),
                    0,
                    r'@@\1##\n'
                ],

                # 回复第128楼，@username
                [
                    r'回复第\d+楼，\s*@(\S{1,16})\b\s*',
                    0,
                    r'@@\1##\n'
                ],

                # 收尾 -----------------------
                
                # 用户名 内容 (无分割线)
                [
                    (r'^(@@\S{1,16}##)\n',
                     r'(?!.*?@@\S{1,16}##)',
                     r'(?!.*?\n', re_separater, r'\s+)',
                     r'(.*)'),
                    red.DOTALL,
                    r'\1\n无内容\n==========\n\2'
                ],

                # 无用户名，一段内容、一条线、一段内容
                # 因为已经处理过 线\s{2,}，所以否定环视里可用\n
                [
                    (r'^(?!.*?@@\S{1,16}##)',
                     r'(?=(.*?\n', re_separater, r'\s+))'
                     r'(?!\1.*?\n', re_separater, r'\s+)',
                     r'\s*(.*?)\s*', re_separater, r'\s+(.*)'),
                    red.DOTALL,
                    r'@@000##\n\2\n==========\n\3'
                ],
              )

    @staticmethod
    def should_me(local_format):
        if local_format == 'Tianya1':
            return True
        else:
            return False

    def has_unhandled_quote(self, reply):
        '''是否包含未处理的引用'''
        p1 = red.re_dict(r'@@\S{1,16}##')
        #p2 = red.re_dict(re_datetime)

        if p1.search(reply.text): # or p2.search(reply.text):
            return True
        else:
            return False

    def process_1(self):
        '''自定义处理'''
        
        # 处理引用
        print('>处理引用')
        r = (r'^(?=(.*@@(\S{1,16})##))',
             r'\1',
             r'.*?',
             r'(?<=\n)',
             r'(?=(.*?(?<=\n)', re_separater, r'\s+))',
             r'(?!\3.*?(?<=\n)', re_separater, r'\s+)',
             r'\s*(.*?)\s*', re_separater, r'\s+(.*)')

        p = red.re_dict(''.join(r), red.DOTALL)

        quote_count = 0
        for rpl in self.rlist:
            rpl.text, n = p.subn(r'回复 \2：\n【引用开始】\4\n【引用结束】\n\5',
                                  rpl.text)
            quote_count += n

#         # 使用'固化分组'处理引用
#         print('>处理引用')
#         r = (r'^(?>.*@@(\S{1,16})##)',
#              r'.*?',
#              r'(?<=\n)',
#              r'(?=(?>.*?(?<=\n)', re_separater, r'\s+)',
#              r'(?!.*?(?<=\n)', re_separater, r'\s+))',
#              r'\s*(.*?)\s*', re_separater, r'\s+(.*)')
#  
#         p = red.re_dict(''.join(r), red.DOTALL)
#  
#         quote_count = 0
#         for rpl in self.rlist:
#             rpl.text, n = p.subn(r'回复 \1：\n【引用开始】\2\n【引用结束】\n\3',
#                                   rpl.text)
#             quote_count += n

        color_p = color.fore_color(quote_count, color.Fore.CYAN)
        print('...处理了{0}条引用'.format(color_p))
