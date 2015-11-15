# coding=utf-8

from BaseProcessor import *

@processor
class Sinabbs1Processor(BaseProcessor):

    # 处理用的正则式list
    # 三个元素分别为：匹配正则，flags，替换
    re_list = (
                # ^RE:title\n
                [
                    r'^RE:[^\n]{1,50}\n',
                    red.I|red.A,
                    r''
                ],

                # 回复6楼 xxxx  的帖子
                [
                    r'^回复\d+楼\s+(\S+)\s*的帖子',
                    red.M,
                    r'回复网友 \1:'
                ],
            
                # [ 本帖最后由 xxxx于 2009-12-10 09:57 编辑 ]
                [
                    (r'\s*\[\s*本帖最后由.*?于\s*'
                     r'\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}\s*编辑\s*\]\s*'
                     ),
                    0,
                    r''
                ],

                # 已处理的引用
                [
                    (r'\A\s*(.*?)\s*'
                     r'^回复\s+(\S+):\s*'
                     r'^【引用开始】\s*(.*?)\s*'
                     r'^【引用结束】\s*(.*?)\s*\Z'
                     ),
                    red.M|red.S,
                    r'回复 \2:\n【引用开始】\3\n【引用结束】\n\1\n\4'
                ],

                # 回复1823楼 xxxx  的帖子
                [
                    r'^回复\d+楼\s*(\S+)\s*的帖子',
                    red.M,
                    r'回复网友 \1:'
                ],

                # 回复 xxx:\n【引用开始】\2\n【引用结束】中的空白
                [
                    r'^回复\s+(.*?):\n【引用开始】\s*(.*?)\s*【引用结束】\s*',
                    red.M|red.S,
                    r'回复 \1:\n【引用开始】\2\n【引用结束】\n'
                ],

                # 前面空白
                [
                    r'^\s*',
                    0,
                    r''
                ],

                # 末尾空白
                [
                    r'\s*$',
                    0,
                    r''
                ],

                # 空回复1
                [
                    (r'^回复\s*\S+\s*写于\s*'
                     r'\d{4}-\d{1,2}-\d{1,2}:\s*$'
                     ),
                    0,
                    r''
                ],

                # 空回复2
                [
                    r'^回复网友\s*\S+:\s*$',
                    0,
                    r''
                ],

                # 空引用
                [
                    r'^\s*回复\s*\S+:\s*【引用开始】\s*【引用结束】\s*$',
                    0,
                    r''
                ],
              )

    @staticmethod
    def should_me(local_format):
        if local_format == 'sinabbs1':
            return True
        else:
            return False
