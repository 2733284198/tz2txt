# coding=utf-8

##  web 到 内部状态1(Reply)
##  tz = web_to_internal(url, pg_count)
##
##  内部状态1 到 编排
##  internal_to_bp(tz, outfile)
##
##  ----------------------------
##
##  编排 到 内部状态2(BPReply)
##  lst = bp_to_internal2(infile)
##
##  处理 内部状态2 
##  lst = process_internal2(lst)
##
##  内部状态2 到 编排
##  internal2_to_bp(lst, outfile)
##
##  ----------------------------
##
##  编排 到 最终
##  bp_to_final(infile, outfile, discard)
##
##  ----------------------------
##
##  统计
##  statistic(all_list)  

from datetime import datetime
import itertools

try:
    import winsound
except:
    has_winsound = False
else:
    has_winsound = True

import color

from red import red
from fetcher import *
from tzdatastruct import *
from BaseProcessor import *
from AbPageParser import *


def save_print(print_str):
    try:
        print(print_str)
    except UnicodeEncodeError:
        for char in print_str:
            try:
                print(char, end='')
            except:
                print('?', end='')
        print()

# 打印编排头信息
def print_bp_head(all_list):
    for one in all_list:
        if isinstance(one, str):
            if one.startswith('<tiezi>'):
                print_str = one[len('<tiezi>'):]
                save_print(print_str)
        elif isinstance(one, BPReply):
            break
    print()

# 统计
def statistic(all_list):
    processor = BaseProcessor()
    
    rlist = [one for one in all_list if isinstance(one, BPReply)]

    processor.set_rlist(rlist)
    processor.statistic()

def process_internal2(all_list):
    '''处理中间形式2'''
    
    def get_processor(all_list):
        '''得到处理器'''
        processor = None
        if all_list:
            p = red.re_dict(r'<processor:\s*(.*?)\s*>')
            m = p.search(all_list[0])
            if m:
                local_processor = m.group(1)
                processor = BaseProcessor.get_processor(local_processor)

        return processor

    # 找到处理器
    processor = get_processor(all_list)
    if not processor:
        print('编排文本的首行没有指定自动处理器，不做处理\n例如：<processor: sample>')
        return all_list

    rlist = [one for one in all_list if isinstance(one, BPReply)]

    print('共有{0}条回复，选择了{1}条回复。\n'.format(
                        len(rlist),
                        sum(1 for i in rlist if i.select)
                        )
          )

    processor.set_rlist(rlist)
    processor.process()

    print('共有{0}条回复，选择了{1}条回复。\n'.format(
                        len(rlist),
                        sum(1 for i in rlist if i.select and i.suggest)
                        )
          )
    
    return all_list

def reply_to_bp(reply, select):
    '''回复->编排，鸭子类型'''
    mark = '█' if select else ''
        
    t = ('<time>◇◆◇◆◇◆◇◆◇◆◇ <',
         reply.time.strftime('%Y-%m-%d  %H:%M:%S  %w'),
         '> ◇◆◇◆◇◆◇◆◇◆◇\n',
         reply.text,
         '\n<mark>══════保留标记：', mark
         )
    return ''.join(t)

def internal2_to_bp(all_list, outfile):
    '''中间形式2 到 编排文本'''
    def to_bp(obj):
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, BPReply):
            s = obj.select and obj.suggest
            return reply_to_bp(obj, s)
    
    if not all_list:
        print('无法处理，请检查输入文件是否为编排文本')
        return False
    
    with open(outfile, 'w', encoding='gb18030', errors='replace') as out:
        write_list = (to_bp(one) for one in all_list)
        write_buffer = '\n'.join(write_list)
   
        out.write(write_buffer)
    return True

def bp_to_internal2(infile):
    '''编排文本 到 中间形式2'''
    all_list = list()

    # 读入编排
    with open(infile, encoding='gb18030', errors='replace') as bp:
        pattern = red.re_dict(r'<(\d{4}-\d\d-\d\d\s+\d\d:\d\d:\d\d)')
        dt = lambda s:datetime.strptime(s, '%Y-%m-%d  %H:%M:%S')
        
        temp = list()
        temp_date = None
        in_reply = False

        try:
            bptext = bp.readlines()
            for line in bptext:
                line = line.rstrip('\n')
                
                if line.startswith('<time>'):
                    if in_reply == True:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<mark>行')
                        break
                    m = pattern.search(line)
                    if not m:
                        print('无法解析日期')
                        break
                    temp_date = dt(m.group(1))
                    in_reply = True

                elif line.startswith('<mark>'):
                    if in_reply == False:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<time>行')
                        break
                    if line.endswith('█'):
                        select = True
                    else:
                        select = False
                    # 添加回复
                    rpl = BPReply(temp_date, '\n'.join(temp), select)
                    all_list.append(rpl)
                    
                    temp.clear()
                    in_reply = False

                elif in_reply:
                    temp.append(line)

                elif not in_reply:
                    all_list.append(line)
                    
            if in_reply == True:
                print('格式错误：最后一个回复文本的前后包括标志不配对。')

            del bptext
        except UnicodeError as e:
            print('\n文件编码错误，请确保输入文件为GBK或GB18030编码。')
            print('异常信息：', e, '\n')

    return all_list

def count_chinese(string):
    '''统计汉字字数'''
    count = 0
    for c in string:
        c = ord(c)
        # CJK统一汉字          20924
        # CJK统一汉字扩充A     6582
        
        # 3块CJK兼容汉字       467
        
        # CJK统一汉字扩充B     42711
        # CJK兼容汉字补充      542
        if 0x4E00 <= c <= 0x9FBB or \
           0x3400 <= c <= 0x4DB5 or \
           \
           0xF900 <= c <= 0xFA2D or \
           0xFA30 <= c <= 0xFA6A or \
           0xFA70 <= c <= 0xFAD9 or \
           \
           0x20000 <= c <= 0x2A6D6 or \
           0x2F800 <= c <= 0x2FA1D:
            count += 1
    return count

def bp_to_final(infile, outfile, discard='', label=0):
    '''编译 编排to最终、丢弃'''
    class placeholder:
        def __init__(self, posi=0, pagenum=0, show=False):
            self.posi = posi
            self.pagenum = pagenum
            self.show = show

    def is_not_empty(lst):
        for i in lst:
            yield i.strip() != ''
    
    info_list = list()
    holder_list = [placeholder()]
    
    text_list = list()
    abandon_list = list()
    
    pickcount, allcount = 0, 0

    # 用于把 [img]http://img3.laibafile.cn/p/m/1234567.jpg[/img]
    # 替换成 【图片：1234567.jpg】
    picr = (r'\[img\s*(\d+|)\].*?\[/img\]')
    pattern = red.re_dict(picr)
    
    # 提取页号
    re_pagenum = red.re_dict(r'^<page>页号:\s*(\d+)\s*$')
    
    # 提取时间
    p_time = (r'^<time>[^<]*<\d\d(\d\d-\d{1,2}-\d{1,2})\s+'
              r'(\d{1,2}:\d{1,2})')
    re_time = red.re_dict(p_time)

    # 读取编排文本
    with open(infile, encoding='gb18030', errors='replace') as i:
        in_reply = False
        temp = list()
        
        current_page = 0
        current_time = ''

        try:
            bptext = i.readlines()
            for line in bptext:
                if line.startswith('<time>'):
                    if in_reply == True:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<mark>行')
                        break
                    in_reply = True
                    
                    # current_time
                    if label == 2:
                        m = re_time.search(line)
                        if m:
                            current_time = m.group(1) + ' ' + m.group(2)
                        else:
                            current_time = ''
                    
                elif line.startswith('<mark>'):
                    if in_reply == False:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<time>行')
                        break
                                           
                    if line.endswith('█\n') or line.endswith('█'):
                        pickcount += 1
                        
                        if label == 0:
                            pass
                        elif label == 1:
                            holder_list[-1].show = True
                        elif label == 2:
                            floor_label = ('№.%d ☆☆☆'
                                           ' 发表于%s  P.%d '
                                           '☆☆☆\n'
                                           '-------------------------'
                                           '-------------------------'
                                           '\n')
                            floor_label = floor_label % \
                                (pickcount, current_time, current_page)
                            text_list.append(floor_label)
                            
                        text_list.extend(temp)
                        text_list.append('\n')

                    elif any(is_not_empty(temp)):
                        abandon_list.extend(temp)
                        abandon_list.append('∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞\n\n')
                        
                    temp.clear()
                    allcount += 1
                    in_reply = False
                    
                elif in_reply:
                    line = pattern.sub(r'【一张图片\1】', line)
                    temp.append(line)

                # 由于上一个elif，以下必定not in_reply
                elif not text_list and not abandon_list and \
                     line.startswith('<tiezi>'):
                    info_list.append(line[len('<tiezi>'):])
                
                elif label != 0:
                    m = re_pagenum.search(line)
                    if m:
                        current_page = int(m.group(1))
                        if label == 1:
                            text_list.append('')
                            holder = placeholder(len(text_list)-1,
                                                 current_page
                                                 )
                            holder_list.append(holder)

            if in_reply == True:
                print('格式错误：最后一个回复文本的前后包括标志不配对。')

            del bptext
        except UnicodeError as e:
            print('\n文件编码错误，请确保输入文件为GBK或GB18030编码。')
            print('异常信息：', e, '\n')
    
    # 页码 辅助格式
    if label == 1:
        for holder in holder_list[1:]:
            if holder.show:
                page_label = ('☆☆☆☆☆'
                              ' 进入第%d页 '
                              '☆☆☆☆☆\n'
                              '----------------'
                              '----------------'
                              '\n\n') % holder.pagenum
                text_list[holder.posi] = page_label

    color_p1 = color.fore_color(allcount, color.Fore.YELLOW)
    color_p2 = color.fore_color(pickcount, color.Fore.YELLOW)
    print('共有{0}条回复，选择了其中{1}条回复'.format(color_p1, color_p2))

    # 写入最终文本
    with open(outfile, 'w', encoding='gb18030', errors='replace') as o:
        # 连接
        if info_list:
            s_iter = itertools.chain(info_list, '\n', text_list)
        else:
            s_iter = iter(text_list)
        s = ''.join(s_iter)

        # 连续的多张图片
        s = red.sub(r'(?:【一张图片(\d+|)】\s+){3,}',
                    r'【多张图片\1】\n\n',
                    s)
        
        s = red.sub(r'(?:【一张图片(\d+|)】\s+){2}',
                    r'【两张图片\1】\n\n',
                    s)
        chinese_ct = count_chinese(s)

        # 写入
        o.write(s)

    # 丢弃文本
    if discard and abandon_list:
        with open(discard, 'w', encoding='gb18030', errors='replace') as a:
            s_iter = itertools.chain(info_list, '\n', abandon_list)
            s = ''.join(s_iter)
            a.write(s)
            
    return chinese_ct, info_list

def internal_to_bp(tz, outfile):
    '''
    内部形式 到 编排
    返回(标题,输出文件字节)
    '''
    
    def page_to_g(page, user):
        '''一页，返回：文本，摘取回复数，总回复数'''
        rpls = [reply_to_bp(r, True)
                    for r in page.replys
                    if r.author == user]
        
        pickcount = len(rpls)
        allcount = len(page.replys)

        if not pickcount:
            return '', 0, allcount
        else:
            # 头信息
            head = ('<page>页号: ', str(page.page_num), '\n',
                    '<page>网址: ', page.url, '\n',
                    '<page>有后页: ', str(page.finished), '\n',
                    '<page>总回复数: ', str(allcount),
                    '  摘取回复数: ', str(pickcount)
                    )
            head = ''.join(head)
            # 头信息 和 文本
            s_iter = itertools.chain((head,), rpls, ('',))
            s = '\n\n'.join(s_iter)
            return s, pickcount, allcount

    def tiezi_to_g(tiezi):
        pgs = [page_to_g(p, tiezi.louzhu) for p in tiezi.pages]
        
        text = (x for x,y,z in pgs if y > 0)
        pickcount = sum(y for x,y,z in pgs)
        allcount = sum(z for x,y,z in pgs)

        color_p1 = color.fore_color(allcount, color.Fore.YELLOW)
        color_p2 = color.fore_color(pickcount, color.Fore.YELLOW)
        print('总回复数: {0}  摘取回复数: {1}'.format(color_p1, color_p2))

        if not pickcount:
            return None
        else:
            # 头信息
            firstpg = tiezi.pages[0]
            lastpg = tiezi.pages[-1]
            
            processor_name = '<processor: ' + tiezi.local_processor + '>\n' \
                             if tiezi.local_processor \
                             else ''

            fmark = '(未下载到末页)' if lastpg.finished else '(已下载到末页)'

            post_time = '<tiezi>发帖时间：' + \
                        firstpg.replys[0].time.strftime('%Y-%m-%d %H:%M') + \
                        '\n' \
                        if firstpg.page_num == 1 and firstpg.replys \
                        else ''
            
            head = (processor_name,
                    '<tiezi>标题：', tiezi.title, '\n',
                    '<tiezi>楼主：', tiezi.louzhu, '\n',
                    post_time,
                    '<tiezi>下载时间：',datetime.now().strftime('%Y-%m-%d %H:%M'),'\n',
                    '<tiezi>起始网址：', tiezi.begin_url, '\n',
                    '起始页号', str(firstpg.page_num),
                    '，末尾页号', str(lastpg.page_num), ' ', fmark, '\n',
                    '总回复数: ', str(allcount),
                    '  摘取回复数: ', str(pickcount), '\n\n'
                    )

            s_iter = itertools.chain(head, text)
            s = ''.join(s_iter)
            return s

    #----------------------------------
    # internal_to_bp(tz, outfile)开始
    #----------------------------------
    if not tz or not tz.pages:
        print('一页也没有，不输出编排文件')
        return '', 0

    text = tiezi_to_g(tz)
    if text == None:
        print('\n没有摘取到回复，不输出文件')
        return '', 0

    with open(outfile, 'w', encoding='gb18030', errors='replace') as o:
        o.write(text)
            
    size = os.path.getsize(outfile)
    print('\n输出文件共{0}字节'.format(format(size,',')))
    
    return tz.title, size

def web_to_internal(url, pg_count):
    '''论坛帖子 到 内部形式'''
    
    # 下载器
    f = Fetcher()
    # 页面解析器
    parser = None
    
    tz = Tiezi()
    dl_count = 0
    while True:
        # 是否下载完指定页数 
        if pg_count >= 0 and dl_count >= pg_count:
            print('下载完指定页数{0}，停止下载\n'.format(pg_count))
            break
        
        # 下载数据
        data = f.fetch_url(url)
        if not data:
            print('无法读取页面：{0}'.format(url))
            break
        
        # 准备解析器
        if not parser:
            parser = AbPageParser.get_parser(url, data)
            if not parser:
                return None
            
            # 检查解析器
            parser.set_page(url, data)
            if not parser.check_parse_methods():
                print(' 可能是网页改版，导致无法提取数据。')
                print(' 请使用“检测新版本”功能检测是否有新程序可用。')
                print()
                return None
            
            # 起始下载页
            tz.begin_url = url
        else:
            # 送数据到解析器
            parser.set_page(url, data)

        # 设置tz的信息
        if not tz.louzhu:
            pub_date = None
            
            tz.title = parser.wrap_get_title()
            tz.louzhu = parser.wrap_get_louzhu()
            
            # 首页1楼作楼主、发帖日期
            if parser.wrap_get_page_num() == 1:
                rplys = parser.wrap_get_replys()
                if rplys:
                    if not tz.louzhu:
                        tz.louzhu = rplys[0].author
                    pub_date = rplys[0].time.strftime('%Y-%m-%d %H:%M')

            # 手工输入楼主ID
            if not tz.louzhu:
                tz.louzhu = input('无法提取楼主ID，请手工输入楼主ID：').strip()

            # 打印帖子信息
            print_str = '标题：%s\n楼主：%s\n' % (tz.title, tz.louzhu) 
            if pub_date != None:
                print_str += '发帖时间：%s\n' % pub_date
            save_print(print_str)

            # 得到本地格式名
            tz.local_processor = parser.get_local_processor()

        next_url = parser.wrap_get_next_pg_url()
        pg_num = parser.wrap_get_page_num()
        # 添加页
        pg = Page(url,
                  pg_num,
                  bool(next_url),
                  parser.wrap_get_replys()
                  )
        tz.add_page(pg)
        dl_count += 1
        print('已下载第{0}页, 共{1}层'.format(pg_num, len(pg.replys)))

        # 帖子的最后一页?
        if not next_url:
            print('\n下载完帖子的最后一页（第{0}页），停止'.format(pg.page_num))
            break
        url = next_url

    count = sum(len(p.replys) for p in tz.pages)

    color_p1 = color.fore_color(len(tz.pages), color.Fore.YELLOW)
    info = '共载入{pg_count}页，共有回复{rpl_count}条'.format(
                            pg_count=color_p1,
                            rpl_count=count
                            )
    print(info)

    # 发出响声
    if has_winsound:
        try:
            winsound.Beep(400, 320) # (frequency, duration)
        except:
            pass

    # 转义编排文本的标签
    def escape_bp_tag(text):
        # 转义编排标签
        text = red.sub(r'^(<(?:time|mark)>)',
                       r'#\1',
                       text,
                       flags=red.MULTILINE)
        
        # 【引用开始】、【引用结束】
        text = red.sub(r'【(引用(?:开始|结束))】',
                       r'[\1]',
                       text)

        # 标记的处理信息
        if text.endswith('【与上一条回复重复】') \
           or text.endswith('【无法处理的回复】'):
            text = text + '#'
        
        return text
    
    for p in tz.pages:
        for r in p.replys:
            r.text = escape_bp_tag(r.text)
    
    return tz
