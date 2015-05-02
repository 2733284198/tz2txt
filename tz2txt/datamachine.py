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

# 打印编排头信息
def print_bp_head(all_list):
    for one in all_list:
        if isinstance(one, str):
            if one.startswith('<tiezi>'):
                try:
                    print(one[len('<tiezi>'):])
                except UnicodeEncodeError as e:
                    print('无法显示一条信息，可能其中包含控制台无法显示的字符。')
                    print('异常信息：', e, '\n')
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

def reply_to_bp(reply, select, append_n=False):
    '''回复->编排，鸭子类型'''
    mark = '█' if select else ''
    n = '\n\n' if append_n else ''
        
    t = ('<time>◇◆◇◆◇◆◇◆◇◆◇ <',
         reply.time.strftime('%Y-%m-%d  %H:%M:%S  %w'),
         '> ◇◆◇◆◇◆◇◆◇◆◇\n',
         reply.text,
         '\n<mark>══════保留标记：', mark, n
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

def bp_to_final(infile, outfile, discard=''):
    '''编译 编排to最终、丢弃'''
    info_list = list()
    text_list = list()
    
    abandon_list = list()
    
    pickcount, allcount = 0, 0

    # 用于把 [img]http://img3.laibafile.cn/p/m/1234567.jpg[/img]
    # 替换成 【图片：1234567.jpg】
    picr = (r'\[img\s*(\d+|)\].*?\[/img\]')
    pattern = red.re_dict(picr)

    # 读取编排文本
    with open(infile, encoding='gb18030', errors='replace') as i:
        in_reply = False
        temp = list()

        try:
            bptext = i.readlines()
            for line in bptext:
                if line.startswith('<time>'):
                    if in_reply == True:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<mark>行')
                        break
                    in_reply = True
                    
                elif line.startswith('<mark>'):
                    if in_reply == False:
                        print('格式错误：回复文本的前后包括标志不配对。\n',
                              '丢失<time>行')
                        break
                                           
                    if line.endswith('█\n') or line.endswith('█'):
                        text_list.extend(temp)
                        text_list.append('\n')
                        pickcount += 1
                    else:
                        abandon_list.extend(temp)
                        abandon_list.append('∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞∞\n\n')
                        
                    temp.clear()
                    allcount += 1
                    in_reply = False
                    
                elif in_reply:
                    line = pattern.sub(r'【一张图片\1】', line)
                    temp.append(line)

                elif not text_list and not abandon_list \
                     and not in_reply and line.startswith('<tiezi>'):
                    info_list.append(line[len('<tiezi>'):])

            if in_reply == True:
                print('格式错误：最后一个回复文本的前后包括标志不配对。')

            del bptext
        except UnicodeError as e:
            print('\n文件编码错误，请确保输入文件为GBK或GB18030编码。')
            print('异常信息：', e, '\n')

    color_p1 = color.fore_color(allcount, color.Fore.YELLOW)
    color_p2 = color.fore_color(pickcount, color.Fore.YELLOW)
    print('共有{0}条回复，选择了其中{1}条回复'.format(color_p1, color_p2))

    if info_list:
        info_list.append('\n')

    # 写入最终文本
    with open(outfile, 'w', encoding='gb18030', errors='replace') as o:
        # 连接
        s_iter = itertools.chain(info_list, text_list)
        s = ''.join(s_iter)

        # 连续的多张图片
        s = red.sub(r'(?:【一张图片(\d+|)】\s+){3,}',
                    r'【多张图片\1】\n\n',
                    s)
        
        s = red.sub(r'(?:【一张图片(\d+|)】\s+){2}',
                    r'【两张图片\1】\n\n',
                    s)

        # 写入
        o.write(s)

    # 丢弃文本
    if discard and abandon_list:
        with open(discard, 'w', encoding='gb18030', errors='replace') as a:
            s_iter = itertools.chain(info_list, abandon_list)
            s = ''.join(s_iter)
            a.write(s)

def internal_to_bp(tz, outfile):
    '''内部形式 到 编排'''
    
    def reply_to_g(reply, user):
        '''一条回复'''
        if reply.author == user:
            return reply_to_bp(reply, True, append_n=True)
        else:
            return None

    def page_to_g(page, user):
        '''一页，返回：文本，摘取回复数，总回复数'''
        rpls = (reply_to_g(r, user) for r in page.replys)
        rpls = [one for one in rpls if one != None]
        pickcount = len(rpls)
        allcount = len(page.replys)

        if not pickcount:
            return '', 0, allcount
        else:
            # 头信息
            head = ('<page>页号: ', str(page.page_num), '\n',
                    '<page>网址: ', page.url, '\n',
                    '<page>是否完结: ', str(page.finished), '\n',
                    '<page>总回复数: ', str(allcount),
                    '  摘取回复数: ', str(pickcount), '\n\n'
                    )
            # 头信息 和 文本
            s_iter = itertools.chain(head, rpls)
            s = ''.join(s_iter)
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

            fmark = '(已完结)' if lastpg.finished else '(未完结)'

            post_time = '<tiezi>发帖日期：' + \
                        firstpg.replys[0].time.strftime('%Y-%m-%d') + \
                        '\n' \
                        if firstpg.page_num == 1 and firstpg.replys \
                        else ''
            
            head = (processor_name,
                    '<tiezi>标题：', tiezi.title, '\n',
                    '<tiezi>楼主：', tiezi.louzhu, '\n',
                    post_time,
                    '<tiezi>下载日期：',datetime.now().strftime('%Y-%m-%d'),'\n',
                    '起始页号', str(firstpg.page_num),
                    '，末尾页号', str(lastpg.page_num), fmark, '\n',
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
        return 0

    text = tiezi_to_g(tz)
    if text == None:
        print('\n没有摘取到回复，不输出文件')
        return 0

    with open(outfile, 'w', encoding='gb18030', errors='replace') as o:
        o.write(text)
            
    size = os.path.getsize(outfile)
    print('\n输出文件共{0}字节'.format(format(size,',')))
    
    return size

def web_to_internal(url, pg_count):
    '''论坛帖子 到 内部形式'''
    
    # 下载器
    fetcher_info = FetcherInfo()
    f = Fetcher(fetcher_info)
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
                print('无法找到页面解析器')
                break
            
            # 检查解析器
            parser.set_page(url, data)
            if not parser.check_parse_methods():
                print('可能是网页改版，导致无法提取数据。')
                break

        # 送数据到解析器
        parser.set_page(url, data)

        # 设置tz的信息
        if not tz.louzhu:             
            tz.title = parser.get_title()
            tz.louzhu = parser.get_louzhu()

            if not tz.louzhu:
                # 第一页第1楼可作为楼主
                if parser.get_page_num() == 1:
                    rplys = parser.get_replys()
                    if rplys:
                        tz.louzhu = rplys[0].author
                # 手工输入
                if not tz.louzhu:
                    tz.louzhu = input('无法提取楼主ID，请手工输入楼主ID：').strip()

            try:
                print('标题：{0}\n楼主：{1}'.format(tz.title, tz.louzhu))
            except UnicodeEncodeError as e:
                print('无法显示标题和楼主ID，可能其中包含控制台无法显示的字符。')
                print('异常信息：', e, '\n')

            # 得到本地格式名
            tz.local_processor = parser.get_local_processor()

        next_url = parser.get_next_pg_url()
        pg_num = parser.get_page_num()
        # 添加页
        pg = Page(url,
                  pg_num,
                  bool(next_url),
                  parser.get_replys()
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
            winsound.Beep(2000, 450)
        except:
            pass

    # 转义编排文本的标签
    def escape_bp_tag(text):
        # 转义编排标签
        text = red.sub(r'^(<(?:time|mark)>)',
                       r'#\1',
                       text,
                       flags=red.MULTILINE)

        # 标记的处理信息
        if text.endswith('【与上一条回复重复】') \
           or text.endswith('【无法处理的回复】'):
            text = text + '#'
        
        return text
    
    for p in tz.pages:
        for r in p.replys:
            r.text = escape_bp_tag(r.text)
    
    return tz
