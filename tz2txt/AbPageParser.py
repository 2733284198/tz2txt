# coding=utf-8

from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse
import html

try:
    import chardet as chardet # as前的模块名可选：cchardet或chardet
except:
    has_chardet = False
else:
    has_chardet = True

from red import red

class AbPageParser(metaclass=ABCMeta):
    '''页面解析 抽象类'''

    # 注册的解析器
    registered = list()

    # 编码列表，用于遍历解码
    decode_list = [
        'utf-8',
        'gb18030',
        'big5',
        ]

    # 编码分析的置信度阈值
    threshold = 0.8

    @staticmethod
    def should_me(url):
        '''返回True表示使用此页面解析器'''
        return False

    @staticmethod
    def get_local_processor():
        '''返回自动处理器的名称'''
        return ''

    @staticmethod
    def get_parser(url):
        '''返回页面解析器'''
        
        for i in AbPageParser.registered:
            if i.should_me(url):
                #print('找到解析器', i)
                return i()
        else:
            print('无法找到处理这个网址的解析器')
            return None

    @staticmethod
    def decode(byte_data, encoding=''):
        '''将byte数据解码为unicode'''
        
        if not encoding:
            if has_chardet:     
                r = chardet.detect(byte_data)
                
                confidence = r['confidence']
                encoding = r['encoding']
                #print(encoding, confidence)
            
                if confidence < AbPageParser.threshold:
                    print('编码分析器异常,编码:{0},置信度{1}.'.format(
                                                            encoding,
                                                            confidence)
                          )
                    return ''
            # 没有chardet，遍历列表
            else:
                for i in AbPageParser.decode_list:
                    try:
                        html = byte_data.decode(i)
                    except UnicodeError as e:
                        pass
                    else:
                        return html
                else:
                    print('无法解码')
                    return ''
         
        return byte_data.decode(encoding, errors='replace')
    
    @staticmethod
    def de_html_char(text):
        '''去掉html转义'''
        t = html.unescape(text)
        
        t = t.replace('•', '·')      # gbk对第一个圆点不支持
        t = t.replace('\xA0', ' ')   # 不间断空格
        t = t.replace('\u3000', ' ') # 中文(全角)空格

        return t

    def __init__(self):
        self.url = ''
        self.html = ''
        
        # 解码byte data到html用的编码
        self.encoding = ''
        
        self.__clear_cache()
    
    def __clear_cache(self):
        '''清空缓存'''
        self.cache_pagenum = None
        self.cache_title = None
        self.cache_louzhu = None
        self.cache_nexturl = None
        self.cache_replys = None

    def set_page(self, url, byte_data):
        '''设置网址和html'''
        self.url = url
        self.html = AbPageParser.decode(byte_data, self.encoding)
        
        self.__clear_cache()
        
    def pre_porecess_url(self, url):
        return url

    def get_hostname(self):
        '''从url得到主机域名'''
        parsed = urlparse(self.url)
        return r'http://' + parsed.netloc
    
    # 5个wrap
    
    def wrap_get_page_num(self):
        if self.cache_pagenum == None:
            self.cache_pagenum = self.get_page_num()
        return self.cache_pagenum
    
    def wrap_get_title(self):
        if self.cache_title == None:
            self.cache_title = self.get_title()
        return self.cache_title
    
    def wrap_get_louzhu(self):
        if self.cache_louzhu == None:
            self.cache_louzhu = self.get_louzhu()
        return self.cache_louzhu
    
    def wrap_get_next_pg_url(self):
        if self.cache_nexturl == None:
            self.cache_nexturl = self.get_next_pg_url()
        return self.cache_nexturl
    
    def wrap_get_replys(self):
        if self.cache_replys == None:
            self.cache_replys = self.get_replys()
        return self.cache_replys

    # 5个抽象get
    
    @abstractmethod
    def get_page_num(self):
        '''页号'''
        pass

    @abstractmethod
    def get_title(self):
        '''标题'''
        pass

    @abstractmethod
    def get_louzhu(self):
        '''楼主'''
        pass

    @abstractmethod
    def get_next_pg_url(self):
        '''下一页url'''
        pass

    @abstractmethod
    def get_replys(self):
        '''返回Reply列表'''
        pass

    def check_parse_methods(self):
        '''检测页面解析器是否正常'''
        
        # 保持这个顺序，因为：
        # get_replys()可能调用get_page_num()
        # get_louzhu()可能调用get_replys()
        
        try:
            self.wrap_get_page_num()
        except Exception as e:
            print('!页面解析器出现异常，无法解析此页面')
            print('!get_page_num():', e, '\n')
            return False

        try:
            self.wrap_get_title()
        except Exception as e:
            print('!页面解析器出现异常，无法解析此页面')
            print('!get_title():', e, '\n')
            return False

        try:
            self.wrap_get_next_pg_url()
        except Exception as e:
            print('!页面解析器出现异常，无法解析此页面')
            print('!get_next_pg_url():', e, '\n')
            return False

        try:
            rpls = self.wrap_get_replys()
            if not rpls:
                raise Exception('异常：回复列表为空')
        except Exception as e:
            print('!页面解析器出现异常，无法解析此页面')
            print('!get_replys():', e, '\n')
            return False

        try:
            self.wrap_get_louzhu()
        except Exception as e:
            print('!页面解析器出现异常，无法解析此页面')
            print('!get_louzhu():', e, '\n')
            return False

        return True

# page-parser decorator
def parser(cls):
    if not issubclass(cls, AbPageParser):
        print('注册页面解析器时出错，{0}不是AbPageParser的子类'.format(cls))
        return cls
    
    if cls not in AbPageParser.registered:
        AbPageParser.registered.append(cls)
    else:
        print('%s already exist in pageparsers' % cls)
    return cls

