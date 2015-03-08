# coding=utf-8

#========================================
#       数据结构
#========================================
class Reply:
    '''一个回复'''
    __slots__ = ('author', 'time', 'text')
        
    def __init__(self, author, time, text):
        self.author = author
        self.time = time
        self.text = text

class BPReply:
    '''一个编排回复'''
    __slots__ = ('time', 'text', 'select', 'suggest')

    def __init__(self, time, text, select, suggest=True):
        self.time = time
        self.text = text
        self.select = select
        self.suggest = suggest

# ---------------------------------------------------

class Page:
    '''一个页面'''
    __slots__ = ('url', 'page_num', 'finished', 'replys')
    
    def __init__(self, url, page_num, finished=False, replys=None):
        self.url = url        
        self.page_num = page_num
        self.finished = finished
        self.replys = list() if replys == None else replys

# ---------------------------------------------------

class Tiezi:
    '''一个帖子'''
    def __init__(self):
        self.title = ''
        self.louzhu = ''
        self.pages = list()
        self.local_format = ''

    def add_page(self, pg):
        self.pages.append(pg)
