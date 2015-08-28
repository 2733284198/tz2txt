# coding=utf-8

import sys
import os, os.path
if sys.version_info < (3, 4, 0):
    print('Python 3.4.0 or above is required')
    print('需要Python 3.4.0以上环境\n')
    if os.name == 'nt':
        os.system('pause')
    exit()

import argparse
import tempfile

import color

from red import red
import datamachine
from tzdatastruct import *
from sites import *

tz2txt_prog = 'tz2txt'
tz2txt_ver = '1.1'  # 内部框架的版本
tz2txt_date = '2015年8月28日'

# 下载帖子、保存编排
def download_till(url, pg_count, outfile):
    # 读入
    tz = datamachine.web_to_internal(url, pg_count)
    # 写编排
    return datamachine.internal_to_bp(tz, outfile)

# 读入编排、统计
def statistic(infile):
    size = os.path.getsize(infile)
    print('编排文件{0}，共{1}字节\n'.format(infile, format(size,',')))
          
    lst = datamachine.bp_to_internal2(infile)
    datamachine.print_bp_head(lst)
    datamachine.statistic(lst)

# 读入编排、自动处理、保存编排
def bp_process_bp(infile, outfile):
    # 文件大小
    size1 = os.path.getsize(infile)
    
    lst = datamachine.bp_to_internal2(infile)
    datamachine.print_bp_head(lst)
    lst = datamachine.process_internal2(lst)
    wrote = datamachine.internal2_to_bp(lst, outfile)

    if wrote:
        size2 = os.path.getsize(outfile)
        print('输入文件{0}字节，输出文件{1}字节'.format(format(size1,','),
                                                    format(size2,',')
                                                    )
              )

# 读入编排、保存纯文本
def compile_txt(infile, outfile, discard=''):
    # 文件大小
    size1 = os.path.getsize(infile)
    size1 = format(size1,',')
    
    datamachine.bp_to_final(infile, outfile, discard)

    size2 = os.path.getsize(outfile)
    size2 = format(size2,',')

    color_p = color.fore_color(size2, color.Fore.MAGENTA)
    print('输入文件{0}字节，输出文件{1}字节'.format(size1, color_p))

# 全自动处理
def auto(url, pg_count, outfile, discard):
    # 创建临时文件
    try:
        f = tempfile.NamedTemporaryFile(delete=False)
        f_name = f.name
        f.close()
    except:
        print('无法创建临时文件')
        return

    # 下载
    outfilesize = download_till(url, pg_count, f_name)
    if not outfilesize:
        # 删除临时文件
        try:
            os.remove(f_name)
        except:
            print('删除临时文件{0}时出错'.format(f_name))
        return
    
    print('\n ===下载完毕，准备自动处理===\n')

    # 自动处理
    bp_process_bp(f_name, f_name)
    print('\n ===自动处理完毕，准备编译===\n')

    # 编译
    compile_txt(f_name, outfile, discard)

    # 删除临时文件
    try:
        os.remove(f_name)
    except:
        print('删除临时文件{0}时出错'.format(f_name))

# 验证url
def is_url(url):
    p = red.re_dict(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', red.IGNORECASE)
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
                              
if __name__ == '__main__':
    color.init()
    print('tz2txt %s\n' % tz2txt_date)

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
                    print('网址格式错误，请检查。')
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
                compile_txt(args.input, args.output, args.discard)

    elif args.subparser == 'a':
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
                    print('网址格式错误，请检查。')
                else:
                    pgnum = '末页' if args.tillnum == -1 else args.tillnum
                    print('网址：{0}\n下载页数：{1}\n输出文件：{2}\n'.format(
                                                    url,
                                                    pgnum,
                                                    args.output)
                          )
                    auto(url, args.tillnum, args.output, args.discard)
    
    else:
        parser.print_help()

    print()

    if os.name == 'nt':
        os.system('pause')

    color.deinit()
