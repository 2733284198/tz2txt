# coding=utf-8

try:
    import regex as re
    vt = tuple(int(i.strip()) for i in re.__version__.split('.'))
    if vt < (2, 4, 85):
        print('regex版本较低:%s, 使用内置re' % re.__version__)
        raise Exception('regex version is low')
    re.DEFAULT_VERSION = re.VERSION0
except:
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
        compiled = red.regexs.get((re_str, flags), 0)
        if compiled == 0:
            try:
                compiled = re.compile(re_str, flags)
            except Exception as e:
                print('编译正则表达式时出现异常:', e)
                print('正则式:', re_str)
                print('模式:', flags, '\n')
                compiled = None
            red.regexs[(re_str, flags)] = compiled

        return compiled

    @staticmethod
    def sub(pattern, repl, string, count=0, flags=0):
        prog = red.re_dict(pattern, flags)
        return prog.sub(repl, string, count=0)