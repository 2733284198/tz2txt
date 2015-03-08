# coding=utf-8

import urllib.request
from urllib.parse import urlparse
import os
import time
import gzip
import zlib
from http.cookiejar import CookieJar

#========================================
#       网络获取
#========================================

class FetcherInfo:
    def __init__(self):
        self.ua = 'tz2txt'
        self.referer = ''
        self.open_timeout = 60
        self.retry_count = 4
        self.retry_interval = 5

class Fetcher:
    '''web获取器'''

    def __init__(self, fetcher_info):
        self.referer = fetcher_info.referer
        self.info = fetcher_info
        
        # ============
        #    opener
        # ============
        
        # no proxy
        proxy = urllib.request.ProxyHandler({})
        # cookie for redirect
        cj = urllib.request.HTTPCookieProcessor(CookieJar())
        # opener
        self.opener = urllib.request.build_opener(proxy, cj)

# 正在使用代理？
#         proxy_dict = urllib.request.getproxies()
#         if proxy_dict:
#             print('检测到正在使用代理服务器，这可能降低网络性能。')
#             print('代理服务器信息:')
#             for k, v in proxy_dict.items():
#                 print('协议: {0:<7} 代理服务器: {1}'.format(k, v))
#             print()

    def save_file(self, url, local_path):
        if os.path.exists(local_path):
            print(local_path, '文件已存在')
            return
        
        byte_data = fetch_url(url)
        with open(local_path, 'wb') as f:
            f.write(byte_data)

    def get_hostname(self, url):
        '''从url得到主机域名'''
        head = r'https://' if url.startswith(r'https://') else r'http://'
        parsed = urlparse(url)
        
        return head + parsed.netloc + r'/'

    def fetch_url(self, url):
        '''返回bytes'''
        # 重试次数
        retry = self.info.retry_count

##        # referer
##        if not self.referer or self.referer not in url:
##            self.referer = self.get_hostname(url)

        # request对象
        req = urllib.request.Request(url)
        req.add_header('Referer', self.referer)
        req.add_header('User-Agent', self.info.ua)

        # 重试用的循环
        while True:
            try:
                # r是HTTPResponse对象
                r = self.opener.open(req,
                                timeout=self.info.open_timeout
                                )
                ret_data = r.read()

                # decompress
                contentenc = r.getheader('Content-Encoding', '')
                if not contentenc:
                    return ret_data
                else:
                    contentenc = contentenc.lower()
                    if 'gzip' in contentenc:
                        ret_data = gzip.decompress(ret_data)
                    elif 'deflate' in contentenc:
                        try:
                            # first try: zlib
                            ret_data = zlib.decompress(ret_data, 15)
                        except:
                            # second try: raw deflate
                            ret_data = zlib.decompress(ret_data, -15)
                    return ret_data

            except Exception as e:
                print('! 下载时出现异常')
                print('! 可能是网址错误、服务器抽风、下载超时、解压缩失败等等')
                print('! 详细异常信息:', type(e), '\n', e, '\n')

            retry -= 1
            if retry <= 0:
                break
            
            print('{0}秒后重试，剩余重试次数：{1}次\n'.
                  format(self.info.retry_interval, retry)
                  )
            time.sleep(self.info.retry_interval)

        print('重试次数用完，下载失败')
        return b''
