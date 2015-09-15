# coding=utf-8

import re

#========================================
#       正则字典
#========================================

class red:
    A = re.A
    ASCII = re.ASCII

    DEBUG = re.DEBUG

    I = re.I
    IGNORECASE = re.IGNORECASE

    L = re.L
    LOCALE = re.LOCALE

    M = re.M
    MULTILINE = re.MULTILINE

    S = re.S
    DOTALL = re.DOTALL

    X = re.X
    VERBOSE = re.VERBOSE
    
    # 正则字典
    regexs = dict()

    @staticmethod
    def re_dict(re_str, flags=0):
        '''使正则式只编译一次'''
        compiled = red.regexs.get((re_str, flags))
        if compiled == None:
            try:
                compiled = re.compile(re_str, flags)
                red.regexs[(re_str, flags)] = compiled
            except Exception as e:
                print('编译正则表达式时出现异常:', e)
                print('正则式:', re_str)
                print('模式:', flags, '\n')
                compiled = None

        return compiled

    @staticmethod
    def sub(pattern, repl, string, count=0, flags=0):
        prog = red.re_dict(pattern, flags)
        return prog.sub(repl, string, count=0)