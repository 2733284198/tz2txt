#! /usr/bin/python3
# coding=utf-8
# 本程序用于自动检测最新版本

import os
from red import red
import webbrowser

from fetcher import *
from tz2txt import tz2txt_date

def check():
    fetcher_info = FetcherInfo()
    f = Fetcher(fetcher_info)
    url = 'https://raw.githubusercontent.com/animalize/tz2txt/master/tz2txt/tz2txt.py'
    
    try:
        data = f.fetch_url(url)
    except:
        raise Exception('无法下载“包含版本信息的网页”')
    
    try:
        html = data.decode('utf-8')
    except:
        raise Exception('无法用utf-8解码“包含版本信息的网页”')
    
    p = r'''tz2txt_date\s*=\s*['"]([^'"]+)['"]'''
    r = red.re_dict(p, red.DOTALL)
    m = r.search(html)
    if not m:
        raise Exception('无法从“包含版本信息的网页”提取最新的版本号')
    
    newver = m.group(1)
    download_url = 'https://github.com/animalize/tz2txt'
    
    return newver, download_url

def main():
    newver, download_url = check()
    
    if newver > tz2txt_date:
        print('发现新版本：%s' % newver)
        
        answer = input('是否打开浏览器进入下载页面？(输入y打开，否则退出)')
        if answer.strip().lower() == 'y': 
            try:
                print('\n正在尝试调用浏览器打开： %s' % download_url)
                webbrowser.open_new_tab(download_url)
            except:
                s = ('无法调用浏览器打开下载页面。\n'
                     '请手动打开下载页面： ' + download_url)
                raise Exception(s)
    elif newver != tz2txt_date:
        print('当前版本 比 网上版本(%s)新' % newver)
    else:
        print('检测完毕，正在使用的是最新版。\n')

if __name__ == '__main__':
    print('\n准备检测tz2txt的最新版本，当前版本是：%s\n' % tz2txt_date)
    
    try:
        main()
    except Exception as e:
        print('出现错误：', e)
        print()
    finally:
        if os.name == 'nt':
            print()
            os.system('pause')
