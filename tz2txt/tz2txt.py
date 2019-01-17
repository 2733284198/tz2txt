#! /usr/bin/python3
# coding=utf-8

tz2txt_prog = 'tz2txt'
tz2txt_ver  = '1.4'         # 内部框架的版本
tz2txt_date = '2019-1-17'   # 最后更新日期

import sys
import os, os.path
if sys.version_info < (3, 4, 0):
    print('Python 3.4.0 or above is required')
    print('需要Python 3.4.0以上环境\n')
    if os.name == 'nt':
        os.system('pause')
    exit()
from io import StringIO

import color
from red import red
import datamachine
from tzdatastruct import *
import sites

# read to StringIO object
def read_input(filename):
    try:
        with open(filename, 
                  encoding='gb18030', errors='replace') as i:
            text = i.read()
        infile = StringIO(text)  
    except Exception as e:
        print('读取文件时异常:', e)
        return None
    else:
        return infile
        
# write StringIO object
def write_output(output, filename, show_size=True):
    if output == None:
        return
    
    text = output.getvalue()
    if not text:
        return
    
    try:
        with open(filename, 'w', 
                  encoding='gb18030', errors='replace') as o:
            o.write(text)
    except Exception as e:
        print('输出文件时异常:', e)
    else:
        if show_size:
            size = os.path.getsize(filename)
            print('输出文件共{0}字节'.format(format(size,',')))
    finally:
        output.close()

# 下载帖子、保存编排，返回(标题,输出文件字节数)
def download_till(url, pg_count, outfile, automode=False):
    # 读入
    tz = datamachine.web_to_internal(url, pg_count)
    if tz == None:
        return None, None
    
    # 得到编排
    output, title = datamachine.internal_to_bp(tz)

    # 写文件
    if automode:
        return output, title
    else:
        write_output(output, outfile)
        return None, None

# 读入编排、统计
def statistic(infile, automode=False):
    if not automode:
        size = os.path.getsize(infile)
        print('编排文件{0}，共{1}字节\n'.format(infile, format(size,',')))
        infile = read_input(infile)
        if infile == None:
            return
          
    lst = datamachine.bp_to_internal2(infile)
    
    datamachine.print_bp_head(lst)
    datamachine.statistic(lst)

# 读入编排、自动处理、保存编排
def bp_process_bp(infile, outfile, automode=False):
    if not automode:
        # 文件大小
        size1 = os.path.getsize(infile)
        infile = read_input(infile)
        if infile == None:
            return None
    
    # read to internal2
    lst = datamachine.bp_to_internal2(infile)
    
    if not automode:
        datamachine.print_bp_head(lst)
    
    # process
    lst = datamachine.process_internal2(lst)
    
    # get output
    output = datamachine.internal2_to_bp(lst)
    if output == None:
        return None
    
    # 写文件
    if automode:
        return output
    else:
        write_output(output, outfile, show_size=False)
        
        size2 = os.path.getsize(outfile)
        print('输入文件{0}字节，输出文件{1}字节'.format(format(size1,','),
                                                    format(size2,',')
                                                    )
              )
        return None

# 读入编排、保存纯文本
def compile_txt(infile, outfile, 
                discard='', label='', automode=False):
    if not automode:
        # 文件大小
        size1 = os.path.getsize(infile)
        infile = read_input(infile)
        if infile == None:
            return None, None, None, None
        
    # keep_discard
    keep_discard = True if discard else False
    
    # 格式
    label = label.lower()
    if label == 'page':
        label = 1
    elif label == 'floor':
        label = 2
    else:
        label = 0
    
    output, discard_output, info_list, chinese_ct = \
                datamachine.bp_to_final(infile, keep_discard, label)

    if automode:
        return output, discard_output, info_list, chinese_ct
    else:
        # write file
        write_output(output, outfile, show_size=False)
        
        if discard_output and discard:
            write_output(discard_output, discard, show_size=False)
        
        # format & color
        size1 = format(size1, ',')
        
        size2 = os.path.getsize(outfile)
        size2 = format(size2, ',')
        color_size = color.fore_color(size2, color.Fore.MAGENTA)
        
        chinese_ct = format(chinese_ct, ',')
        color_chinese = color.fore_color(chinese_ct, color.Fore.CYAN)
        
        print('输入文件{0}字节；输出文件{1}字节，约{2}个汉字(不含标点符号)。'.format(
                                                    size1, 
                                                    color_size,
                                                    color_chinese)
              )
    
    return None, None, info_list, chinese_ct

# 全自动处理，返回info_list或None
def auto(url, pg_count, outfile, discard, label, from_gui=False):
    # 下载
    dl_object, title = download_till(url, pg_count,
                                     '', automode=True)
    if dl_object == None:
        return None, None, None, None, None
    
    print('\n ===下载完毕，准备自动处理===\n')

    # 自动处理
    bp_object = bp_process_bp(dl_object, '', automode=True)
    print('\n ===自动处理完毕，准备编译===\n')
    
    # 编译
    if from_gui:
        discard = 'from_gui'
    output, discard_output, info_list, chinese_ct = \
        compile_txt(bp_object, '', discard, label, automode=True)
        
    if not from_gui:
        # write file
        write_output(output, outfile, show_size=False)
        
        if discard_output:
            write_output(discard_output, discard, show_size=False)
        
        # format & color        
        size2 = os.path.getsize(outfile)
        size2 = format(size2, ',')
        color_size = color.fore_color(size2, color.Fore.MAGENTA)
        
        chinese_ct = format(chinese_ct, ',')
        color_chinese = color.fore_color(chinese_ct, color.Fore.CYAN)
        
        print('输出文件{0}字节，约{1}个汉字。'.format(
                                                    color_size,
                                                    color_chinese)
              )
    else:
        return output, discard_output, title, info_list, chinese_ct

# 验证url
def is_url(url):
    p = red.re_dict(
        r'^https?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', red.IGNORECASE|red.A)
    if p.match(url):
        return True
    else:
        return False

# 是否覆盖文件
def check_file(filename):
    if not os.path.isfile(filename):
        return True
    
    cover = input('输出文件{0}已存在，是否覆盖？(输入y覆盖，否则退出)：'.
                  format(filename)
                  ).strip().lower()
    if cover == 'y':
        print()
        return True
    else:
        return False
                              
def main():
    color.init()
    print('tz2txt 程序版本: %s\n' % tz2txt_date)
    
    pause = True

    import argparse
    parser = argparse.ArgumentParser(prog=tz2txt_prog,
                                     description='用于帮助把帖子转为txt文件'
                                     )
    parser.add_argument('-v', action='version',
                        version=tz2txt_prog+' '+tz2txt_ver+' '+tz2txt_date
                        )
    subparsers = parser.add_subparsers(dest='subparser', help='子功能')

    # 下载成编排d
    parser_d = subparsers.add_parser('d', help='下载帖子到‘编排txt’')
    parser_d.add_argument('-u',
                          type=str, help='帖子网址',
                          metavar='网址',
                          default='',
                          dest='url')
    parser_d.add_argument('-t',
                          type=int, help='下载页数，-1为到尾页',
                          metavar='页数',
                          default=-1,
                          dest='tillnum')
    parser_d.add_argument('-o',
                          type=str, help='输出文件名',
                          metavar='文件名',
                          dest='output')

    # 统计编排s
    parser_s = subparsers.add_parser('s', help='统计‘编排txt’的信息')
    parser_s.add_argument('-i',
                          type=str, help='输入的编排文件',
                          metavar='文件名',
                          dest='input')

    # 处理编排p
    parser_p = subparsers.add_parser('p', help='自动处理‘编排txt’')
    parser_p.add_argument('-i',
                          type=str, help='输入的编排文件',
                          metavar='文件名',
                          dest='input')
    parser_p.add_argument('-o',
                          type=str, help='输出的编排文件',
                          metavar='文件名',
                          dest='output')
    
    # 编译c
    parser_c = subparsers.add_parser('c', help='编译‘编排txt’到‘纯txt’')
    parser_c.add_argument('-i',
                          type=str, help='输入的编排文件',
                          metavar='文件名',
                          dest='input')
    parser_c.add_argument('-o',
                          type=str, help='输出的最终txt文件',
                          metavar='文件名',
                          dest='output')
    parser_c.add_argument('-d',
                          type=str, help='输出遗弃内容到txt文件',
                          metavar='文件名',
                          default='',
                          dest='discard')
    parser_c.add_argument('-w',
                          type=str, help='是否有位置信息，默认为没有',
                          metavar='page或floor',
                          default='',
                          dest='label')

    # 全自动处理a
    parser_a = subparsers.add_parser('a', help='全自动生成最终文本')
    parser_a.add_argument('-u',
                          type=str, help='帖子网址',
                          metavar='网址',
                          default='',
                          dest='url')
    parser_a.add_argument('-t',
                          type=int, help='下载页数，-1为到尾页',
                          metavar='页数',
                          default=-1,
                          dest='tillnum')
    parser_a.add_argument('-o',
                          type=str, help='输出的最终txt文件',
                          metavar='文件名',
                          dest='output')
    parser_a.add_argument('-d',
                          type=str, help='输出遗弃内容到txt文件',
                          metavar='文件名',
                          default='',
                          dest='discard')
    parser_a.add_argument('-w',
                          type=str, help='是否有位置信息，默认为没有',
                          metavar='page或floor',
                          default='',
                          dest='label')
    parser_a.add_argument('-s',
                          type=str, help='运行后暂停，等待用户确认',
                          metavar='如传入任意非空字符串，表示不暂停',
                          default='',
                          dest='silence')

    args = parser.parse_args()
    
    if args.subparser == 'd':      
        if args.output == None:
            print('输出文件名不能为空')
        else:                 
            if check_file(args.output):
                if args.url == '':
                    print('请粘贴(或输入)帖子的某页网址，作为起始下载页')
                    url = input('网址：').strip()
                    print()
                else:
                    url = args.url

                if not is_url(url):
                    print('网址格式错误，请检查，网址须以http://或https://开头。')
                else:
                    pgnum = '末页' if args.tillnum == -1 else args.tillnum
                    print('网址：{0}\n下载页数：{1}\n输出文件：{2}\n'.format(
                                                    url,
                                                    pgnum,
                                                    args.output)
                          )
                    download_till(url, args.tillnum, args.output)

    elif args.subparser == 's':
        if os.path.isfile(args.input):
            statistic(args.input)
        else:
            print('输入文件{0}不存在'.format(args.input))

    elif args.subparser == 'p':
        if args.input == None:
            print('输入文件名不能为空')
        elif args.output == None:
            print('输出文件名不能为空')
        elif not os.path.isfile(args.input):
            print('输入文件{0}不存在'.format(args.input))
        else:
            if check_file(args.output):
                bp_process_bp(args.input, args.output)

    elif args.subparser == 'c':
        if args.input == None:
            print('输入文件名不能为空')
        elif args.output == None:
            print('输出文件名不能为空')
        elif not os.path.isfile(args.input):
            print('输入文件{0}不存在'.format(args.input))
        else:
            if check_file(args.output):
                compile_txt(args.input, args.output, 
                            args.discard, args.label)

    elif args.subparser == 'a':
        pause = args.silence == ''
        
        if args.output == None:
            print('输出文件名不能为空')
        else:
            if check_file(args.output):
                if args.url == '':
                    print('请粘贴(或输入)帖子的某页网址，作为起始下载页')
                    url = input('网址：').strip()
                    print()
                else:
                    url = args.url

                if not is_url(url):
                    print('网址格式错误，请检查，网址须以http://或https://开头。')
                else:
                    pgnum = '末页' if args.tillnum == -1 else args.tillnum
                    print('网址：{0}\n下载页数：{1}\n输出文件：{2}\n'.format(
                                                    url,
                                                    pgnum,
                                                    args.output)
                          )
                    auto(url, args.tillnum, args.output, 
                         args.discard, args.label)
    
    else:
        parser.print_help()

    print()

    if pause and os.name == 'nt':
        os.system('pause')

    color.deinit()

if __name__ == '__main__':
    main()