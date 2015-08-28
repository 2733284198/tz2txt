# coding=utf-8

from red import red
from BaseProcessor import nocode

#========================================
#     在process(p)函数里进行自定义处理
#========================================

@nocode #注释掉此行后，此函数才会生效
def process(processor):
    '''本函数会在process_3之后、后处理之前被调用'''
    print('>custom.process')

    # 去掉短引用
    short_quote(processor, 30, 30, 'or')

##    # 连载过滤
    #regex = r'^[\d一二三四五六七八九十零]{1,3}、?'
    #regex = r'^连载\d+'
    #flags = red.M
    #lianzai_fliter(processor, regex, flags)

# ========= 以下为服务函数 ===========
# 增加新函数时，不要忘记print一下函数功能
# 通常是：把不想要的标为False

def lianzai_fliter(processor, regex, flags):
    '''连载过滤器。注意：只标记suggest，不考虑select'''
    
    print('>连载过滤器\n...正则式:{0}'.format(regex))
    
    pattern = red.re_dict(regex, flags)
    count = 0
    
    for reply in processor.rlist:
        if reply.suggest:
            if not processor.has_quote(reply) \
               and pattern.search(reply.text):
                count += 1
            else:
                reply.suggest = False

    print('...选择了{0}条回复作为连载'.format(count))

def short_quote(processor, quote_len, reply_len, logic='or'):
    '''处理短引用'''
    
    # 返回True表示保留，返回False表示去掉
    def deal_logic(t):
        if logic == 'and':
            return t[0] >= quote_len and t[1] >= reply_len
        else:
            return t[0] >= quote_len or t[1] >= reply_len

    logic = logic.lower()
    if logic == 'and':
        template = '>筛除短引用回复\n...保留:引用部分>={0} 且 回复部分>={1}'
    else:
        template = '>筛除短引用回复\n...保留:引用部分>={0} 或 回复部分>={1}'
    print(template.format(quote_len, reply_len))
    
    len_count = 0
    for i in processor.rlist:
        t = processor.reply_len_quote(i)
        if t[0] != -1 and deal_logic(t) == False:
            i.suggest = False
            len_count += 1

    print('...去掉{0}条短引用回复'.format(len_count))
