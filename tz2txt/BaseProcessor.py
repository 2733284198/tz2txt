# coding=utf-8

import statistics
import time

import color

from red import red
from tzdatastruct import *

# 装饰器，用于process_x
def nocode(fn):
    fn.nocode = True
    return fn

class BaseProcessor():
    '''处理器 基类'''

    # 注册的处理器
    registered = list()

    # 处理用的正则式list
    # 三个元素分别为：匹配正则，flags，替换
    re_list = (
                # 示例
                [
                    r'',
                    0,
                    r''
                ],
                )     

    @staticmethod
    def should_me(local_processor):
        if local_processor == 'null':
            return True
        else:
            return False

    @staticmethod
    def get_processor(local_processor):
        '''得到自动处理器'''
        for i in BaseProcessor.registered:
            if i.should_me(local_processor):
                #print('找到处理器', i)
                return i()
        else:
            print('无法找到本地格式为{0}的处理器'.format(local_processor))
            return None

    def __init__(self):
        self.rlist = None

    def set_rlist(self, rlist):
        self.rlist = rlist

    def has_unhandled_quote(self, reply):
        '''是否包含未处理的引用，返回True的回复不会被select'''
        return False

    @staticmethod                                  
    def has_quote(reply):
        '''是否包含引用'''
        p = red.re_dict(r'^.*?【引用开始】.*?【引用结束】')

        if p.search(reply.text):
            return True
        else:
            return False

    @staticmethod
    def reply_len_quote(reply):
        '''一条回复的字数，返回(引用字数，回复字数，前两者之和 或 是无引用的长度)'''
        all_len = len(reply.text)
        tag_len = len('【引用开始】')
        
        p1 = reply.text.find('【引用开始】')
        p2 = reply.text.find('【引用结束】')
        
        if p1 == -1 and p2 == -1:
            return -1, -1, all_len
        
        elif p1 != -1 and p2 != -1 and p2 > p1:
            return p2-p1-tag_len, \
               all_len-p2-tag_len, \
               all_len-p1-2*tag_len

        else:
            print('【引用开始】和【引用结束】不配对')
            return -1, -1, all_len

    @staticmethod
    def append_note(text, note):
        '''添加处理说明'''
        if not text.endswith(note):
            text += '\n' + note
        return text

    def do_re_list(self):
        '''用re_list进行替换处理'''
        print('>用正则式列表替换')
        
        # 编译
        for i in self.re_list:
            i.append(red.re_dict(''.join(i[0]), i[1]))

        process_count = 0
        for rpl in self.rlist:
            #i = 0
            for r in self.re_list:
                rpl.text, n = r[3].subn(r[2], rpl.text)
                process_count += 1 if n > 0 else 0

                #if '某些文字' in rpl.text:
                #    print(rpl.text, '\n', i, '>>>>>>>')
                #    i += 1
        print('...做了{0}次替换'.format(process_count))

    def mark_empty(self):
        '''标记空回复'''
        print('>标记空白回复：')
        
        p = red.re_dict(r'^\s*$')
        blank_count = 0
        
        for rpl in self.rlist:
            if p.match(rpl.text):
                rpl.suggest = False
                blank_count += 1

        if blank_count:
            color_p = color.fore_color(blank_count, color.Fore.RED)
        else:
            color_p = color.fore_color(blank_count, color.Fore.GREEN)

        print('...标记了{0}个空白回复'.format(color_p))
        
    def mark_reduplicate(self):
        '''标记相邻重复'''        
        print('>检查相邻重复：')

        last_reply = None
        reduplicate_list = []
        r = red.re_dict('^\s*$')

        # 查找重复
        for rpl in self.rlist:
            if last_reply and last_reply.text == rpl.text and \
               not r.match(rpl.text):
                reduplicate_list.append(rpl)
            last_reply = rpl

        # 处理重复
        for i in reduplicate_list:
            i.text = self.append_note(i.text, '【与上一条回复重复】')
            i.suggest = False

        reduplicate_count = len(reduplicate_list)
        if reduplicate_count:
            color_p = color.fore_color(reduplicate_count, color.Fore.RED)
        else:
            color_p = color.fore_color(reduplicate_count, color.Fore.GREEN)

        print('...标记了{0}个重复回复'.format(color_p))

    def mark_cantdeal(self):
        '''标记无法处理'''       
        print('>查找无法处理的引用')
        
        quote_count = 0

        for rpl in self.rlist:
            if self.has_unhandled_quote(rpl):
                rpl.text = self.append_note(rpl.text, '【无法处理的回复】')
                rpl.suggest = False
                quote_count += 1

        if quote_count:
            color_p = color.fore_color(quote_count, color.Fore.RED)
        else:
            color_p = color.fore_color(quote_count, color.Fore.GREEN)
            
        print('...标记了{0}个无法处理引用的回复'.format(color_p))

    @nocode
    def process_1(self):
        '''自定义处理1'''
        pass
    
    @nocode
    def process_2(self):
        '''自定义处理2'''
        pass
    
    @nocode
    def process_3(self):
        '''自定义处理3'''
        pass

    def process(self):
        '''处理流程'''
        
        if self.rlist == None:
            print('rlist为None，不能处理')
            return

        # 预处理
        if self.re_list != BaseProcessor.re_list:
            print('预处理开始：')
            t1 = time.perf_counter()
            self.do_re_list()
            t2 = time.perf_counter()
            print('预处理结束，运行了%.5f秒\n' % (t2-t1))

        if not hasattr(self.process_1, 'nocode'):
            print('Process 1开始:')
            t1 = time.perf_counter()
            self.process_1()
            t2 = time.perf_counter()
            print('Process 1结束，运行了%.5f秒\n' % (t2-t1))
        
        if not hasattr(self.process_2, 'nocode'):
            print('Process 2开始:')
            t1 = time.perf_counter()
            self.process_2()
            t2 = time.perf_counter()
            print('Process 2结束，运行了%.5f秒\n' % (t2-t1))

        if not hasattr(self.process_3, 'nocode'):
            print('Process 3开始:')
            t1 = time.perf_counter()
            self.process_3()
            t2 = time.perf_counter()
            print('Process 3结束，运行了%.5f秒\n' % (t2-t1))
        
        # custom.py的process(p)函数
        try:
            from custom import process as custom_process
        except:
            print('无法import custom.py里的process(p)函数')
        else:
            if not hasattr(custom_process, 'nocode'):
                print('custom.py的process(p)函数开始:')
                t1 = time.perf_counter()
                custom_process(self)
                t2 = time.perf_counter()
                print('custom.py的process(p)函数结束，运行了%.5f秒\n' % (t2-t1))

        # 后处理
        print('后处理开始：')
        t1 = time.perf_counter()
        
        self.mark_empty()
        self.mark_reduplicate()
        self.mark_cantdeal()
        
        t2 = time.perf_counter()
        print('后处理结束，运行了%.5f秒\n' % (t2-t1))

    def statistic(self):
        '''统计'''      
        # 回复总数 --------------------------
        print('回复总数:', len(self.rlist))

        # 选择的回复数
        selected_count = sum(1 for r in self.rlist if r.select)
        print('选择的回复数:', selected_count)

        print()

        # 字数统计 --------------------------
        print('以下的统计不包括空白、重复和无法处理的回复：\n')

        # 排除不想参与统计的回复
        def should_pick(reply):
            p_space = red.re_dict(r'^\s*$')

            if p_space.match(reply.text):
                return False
            if reply.text.endswith('【与上一条回复重复】'):
                return False
            if reply.text.endswith('【无法处理的回复】'):
                return False
            
            return True
        
        lenlist = [self.reply_len_quote(r)
                   for r in self.rlist if should_pick(r)]

        # 有引用回复 的 引用部分长度
        qlenlist = [x[0] for x in lenlist if x[0] != -1]
        # 有引用回复 的 回复部分长度
        rlenlist = [x[1] for x in lenlist if x[0] != -1]
        # 无引用回复 的 长度
        noqlenlist = [x[2] for x in lenlist if x[0] == -1]
        del lenlist

        def num(lst, func):
            if not lst:
                return 0
            else:
                return func(lst)

        print('           (引用部分 回复部分) 无引用回复')
        print('　总　数　:   {0:<8}  +       {1:<8} = {2}'.format(
                        len(qlenlist),
                        len(noqlenlist),
                        len(qlenlist) + len(noqlenlist)
                        )
              )
        print('最长的字数:   {0:<8} {1:<8} {2:<8}'.format(
                        num(qlenlist, max),
                        num(rlenlist, max),
                        num(noqlenlist, max)
                        )
              )
        print('字数平均数:   {0:<8.2f} {1:<8.2f} {2:<8.2f}'.format(
                        num(qlenlist, statistics.mean),
                        num(rlenlist, statistics.mean),
                        num(noqlenlist, statistics.mean)
                        )
              )
        print('字数中位数:   {0:<8.0f} {1:<8.0f} {2:<8.0f}'.format(
                        num(qlenlist, statistics.median),
                        num(rlenlist, statistics.median),
                        num(noqlenlist, statistics.median)
                        )
              )
        print('总体标准差:   {0:<8.2f} {1:<8.2f} {2:<8.2f}'.format(
                        num(qlenlist, statistics.pstdev),
                        num(rlenlist, statistics.pstdev),
                        num(noqlenlist, statistics.pstdev)
                        )
              )
        
        # 字数分布 ------------------------------

        # e_table由y=e**x函数生成 x:0.5,1.0,1.5,2.0,2.5,3.0...
        e_table = [0, 7, 12, 20, 33, 55, 90, 148, 245, 403, \
                    665, 1097, 1808, 2981, 4915, 8103, 13360]
        
        # 字数分布函数
        def get_len_distribution(lenlist):
            '''字数分布'''
            table_len = len(e_table)
            count_table = [0 for i in range(table_len+1)]

            for length in lenlist:
                for i in range(table_len):
                    if length < e_table[i]:
                        count_table[i] += 1
                        break
                else:
                    count_table[-1] += 1

            return count_table
        
        # 得到字数分布
        qdis = get_len_distribution(qlenlist)
        rdis = get_len_distribution(rlenlist)
        ndis = get_len_distribution(noqlenlist)       

        # 打印字数分布
        print('\n字数分布')
        print(' '*16, '(引用部分 回复部分) 无引用回复')

        for i in range(1, len(e_table)):
            print('{0:>6}<= x <{1:<5} : {2:<8} {3:<8} {4:<8}'.format(
                                        e_table[i-1],
                                        e_table[i],
                                        qdis[i],
                                        rdis[i],
                                        ndis[i]
                                        )
                  )
        print('{0:>6}<= x        : {1:<8} {2:<8} {3:<8}'.format(
                                        e_table[-1],
                                        qdis[-1],
                                        rdis[-1],
                                        ndis[-1]
                                        )
              )

        print(' '*8,'='*35)
        print(' '*12, '总数 : {0:<8} {1:<8} {2:<8}'.format(
                                                len(qlenlist),
                                                len(rlenlist),
                                                len(noqlenlist)
                                                )
              )
        
# processor decorator
def processor(cls):
    if not issubclass(cls, BaseProcessor):
        print('注册自动处理器时出错，{0}不是BaseProcessor的子类'.format(cls))
        return cls
    
    if cls not in BaseProcessor.registered:
        BaseProcessor.registered.append(cls)
    else:
        print('%s already exist in processors' % cls)
    return cls

@processor # 注册NullProcessor为null的处理器
class NullProcessor(BaseProcessor):
    pass
