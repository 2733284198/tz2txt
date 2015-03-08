# coding=utf-8

from BaseProcessor import *

class SampleProcessor(BaseProcessor):

    # 处理用的正则式list
    # 三个元素分别为：匹配正则，flags，替换
    re_list = (
                # 示例
                [
                    r're',
                    0,
                    r'replace'
                ],
                )

    @staticmethod
    def should_me(local_format):
        if local_format == 'Sample':
            return True
        else:
            return False

    def has_unhandled_quote(self, reply):
        '''是否包含未处理的引用'''
        return False

    def process_1(self):
        '''自定义处理'''
        pass

    def process_2(self):
        '''自定义处理'''
        pass

    def process_3(self):
        '''自定义处理'''        
        pass

# 注册此自动处理器，参数为自动处理器的类名
BaseProcessor.register_me(SampleProcessor)

#别忘了把此文件写进__init__.py里
