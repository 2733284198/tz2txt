#! /usr/bin/python3
# coding=utf-8

# 使用时from txtformat import txtformat
# 本程序参考了DreamEdit的排版规则

import re#gex as re
import html

def de_html_char(text):
    '''html转义字符'''
    
    text = html.unescape(text)
    
    text = text.replace('•', '·')      # gbk对第一个圆点不支持
    text = text.replace('\xA0', ' ')   # 不间断空格
    text = text.replace('\u3000', ' ') # 中文(全角)空格
        
    return text

def replace_with_list(text):
    '''用正则列表替换'''
    
    replace_list = (
       # 1--------------------
    
       # 删除行首行尾空白
       (r'(?:(?<=\n)|^)(?:(?=\s)(?!\n).)+', r''),
       (r'(?:(?=\s)(?!\n).)+(?:(?=\n)|$)', r''),

       # 连续的重复行 变成 一行
       (r'(?:(?<=\n)|^)([^\n]+)\n(?:(?:\1\n)+(?:\1$)?|\1$)', r'\1\n'),

       # 3--------------------
       
       # 两个以上同一字符
       (r'[,\.。]{2,}', r'……'),
       (r'-{2,}', r'——'),

       # 进行字符串替换
       (r',', r'，'),
       (r'\.', r'。'),
       (r'．', r'。'),
       (r';', r'；'),
       (r'!', r'！'),
       (r'\?\?', r'？？'),
       (r'\?', r'？'),
       (r':', r'：'),
       (r'\(', r'（'),
       (r'\)', r'）'),
       (r'－－', r'——'),
       (r'；“', r'：“'),
       #(r'：‘', r'：“'),
       (r'？“', r'？”'),

       # 4--------------------
       
       # 以字符作为依据分段
       # 按照中文的常规，遇到句号，问号，感叹号等等，往往是一句话的结束。
       # 程序不可能像人一样聪明，知道这句话是不是段落的结束，
       # 但是一般来说，这些符号出现在一行的末端的时候，往往就是段落的结束。
       # 第一个的字符组是：作为分段依据的字符。（出现在段尾）
       # 第二个的字符组是：不能作为段首的字符。
       # 与下一条不能同用
       (r'(?=(\n{1,3}))(?<!\n)(?<=[^。？！…」”）])\1(?=[^_a-zA-Z0-9\n])', r''),
       (r'(?=(\n{1,3}))(?<!\n)\1(?=[。？！」”）])', r''),

       # 空行作为分段依据
       # 如果源文件中有空行，则表示一个段落的结束。
       # 相比上一条只是\n{1,3}变成\n，与上一条不能同用
       #(r'(?=\n)(?<!\n)(?<=[^。？！…」”）])\n(?=[^_a-zA-Z0-9\n])', r''),
       #(r'(?=\n)(?<!\n)\n(?=[。？！」”）])', r''),
       
       # 行尾是数字
       (r'(\d)\s*\n+', r'\1'),

       # 5--------------------
       
       # 段间添加空行
       (r'\n+', r'\n\n'),

       # 首尾空白
       (r'^\s+', r''),
       (r'\s+$', r''),
       )
    
    for i in replace_list:
        f = 0 if len(i)==2 else i[2]
        text, n = re.subn(i[0], i[1], text, flags=f)
##        if n:
##            print('正则式: {0}\n替换式: {1}\n替换了{2}次\n'.format(
##                                    i[0],
##                                    i[1],
##                                    n)
##                  )
    return text

#往往很多文章内部的单引号，双引号是乱的，有的是半角、全角混合，有的是左右不分。
#半角全角可以用上面的字符串替换解决，左右不分就需要用到这个矫正功能。
#它使用数数目的方法，遇到的第一个就是左字符，第二个就是右字符。
#如果中间缺了，就会乱了，需要人工干涉后，用段落排版功能对出错段落重排。
def match_pair(text):
    pair_list = (
        ('“', '”'),
        ('‘', '’'),
        ('【', '】'),
        ('《', '》'),
        #('', ''),
        )
    
    return text

def txtformat(text):
    text = de_html_char(text)
    text = replace_with_list(text)

    #text = match_pair(text)

    return text

# --------------------------------------
#       以下为作为单独程序使用时的代码
# --------------------------------------
import shutil
import os
import sys

try:
    import chardet111 as chardet # as前的模块名可选：chardet或cchardet
except:
    has_chardet = False
else:
    has_chardet = True

def decode(data):
    # 遍历解码list
    decode_list = ('gb18030',
                   'utf_8', 'utf_8_sig',
                   'utf_16_le', 'utf_16_be',
                   'utf_32_le', 'utf_32_be',
                   'big5',
                   )
    
    if has_chardet:
        r = chardet.detect(data)
                
        confidence = r['confidence']
        encoding = r['encoding']
        #print(encoding, confidence)
            
        if confidence > 0.8:
            return encoding, data.decode(encoding)
        else:
            print('编码分析器异常,编码:{0},置信度{1}.'.format(
                                                encoding,
                                                confidence)
                    )
            return '', ''
    else:
        for i in decode_list:
            try:
                text = data.decode(i)
            except:
                pass
            else:
                return i, text
        else:           
            print('无法用编码列表解码')
            return '', ''

# 检测文件是否存在
def check_file(filename):
    if os.path.isfile(filename):
        cover = input('输出文件{0}已存在，是否覆盖？(y覆盖，n退出)：'.
                      format(filename)
                      ).strip().lower()
        if cover != 'y':
            return False
    return True

# 主程序
if __name__ == '__main__':
    # 参数
    if len(sys.argv) == 2:
        infile = sys.argv[1]
        outfile = infile + '.bak'
    else:
        print('未指定输入文件名')
        sys.exit()

    # 读入
    with open(infile, 'rb') as i:
        data = i.read()
    if not data:
        print('未读入内容')
        sys.exit()

    # 解码
    charset, text = decode(data)
    if not text:
        print('未能解码')
        sys.exit()        
    print('文件编码:{0}'.format(charset))

    # 排版
    text = txtformat(text)

    # 写文件
    if check_file(outfile):
        try:
            # 复制备份文件
            shutil.copyfile(infile, outfile)
        except:
            print('无法复制为备份文件:{0}'.format(outfile))
        else:
            # 写入原文件
            with open(infile, 'w', encoding=charset) as o:
                o.write(text)
