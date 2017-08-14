import re
import os
import sys
import binascii
import argparse

try:
    import winsound
except:
    winsound = None

from fetcher import *


def get_tieze_head(content):
    p_head = (r'<tiezi>标题：([^\n]+)\n'
              r'<tiezi>楼主：([^\n]+)\n'
              r'(?:<tiezi>发帖时间：([^\n]+)\n)?'
              r'<tiezi>下载时间：([^\n]+)\n'
              r'<tiezi>起始网址：([^\n]+)\n'
              )
    sub_head = (r'<b>标题：\1</b><br>'
                r'楼主：\2<br>'
                r'发帖时间：\3<br>'
                r'下载时间：\4<br>'
                r'起始网址：<a href="\5" target=_blank>\5</a><br>'
                )

    m = re.search(p_head, content)
    if m:
        head = m.expand(sub_head)
    else:
        head = ''

    return head


def process_replys(reply_list, save_dir):
    p_img = r'\[img\s*\d*\](.*?)\[/img\]'

    pic_count = 1
    pic_list = list()  # 值为 ('路径', 'url')
    pic_url_fn = dict()

    for i in range(len(reply_list)):
        s = reply_list[i]

        new = ''
        last = 0

        while True:
            m = re.search(p_img, s[last:], re.I)
            if m is None:
                break

            new += s[last:last + m.start(0)]
            last = last + m.end(0)

            # 提取图片url
            url = m.group(1)

            # 重复的图片
            if url in pic_url_fn:
                fn = pic_url_fn[url]
            else:
                # 得到图片的本地文件名
                crc = binascii.crc32(url.encode('utf-8'))
                crc = '{:08x}'.format(crc)

                m = re.search(r'^.*(\.\w+)$', url)
                if m:
                    fn = str(pic_count) + '_' + crc + m.group(1)
                else:
                    fn = str(pic_count) + '_' + crc + '.jpg'

                pic_count += 1

                # 去重字典
                pic_url_fn[url] = fn

                # 下载列表
                path = os.path.join(save_dir, fn)
                pic_list.append((path, url))

            # 替换html
            new += '<img src="%s" />' % fn

        # 最后一段
        new += s[last:]

        reply_list[i] = new

    # join
    htmls = '<br><br>'.join(reply_list)
    # 换行
    htmls = htmls.replace('\n', '<br>\n')

    return htmls, pic_list


def download_pics(refer, pic_list):
    # 下载器
    fetcher_info = FetcherInfo()
    fetcher_info.referer = refer
    fetcher = Fetcher(fetcher_info)

    pic_count = 1
    pic_all = len(pic_list)

    for path, url in pic_list:
        if not os.path.exists(path):
            print('(%d/%d)保存图片:' % (pic_count, pic_all), url)

            fetcher.save_file(url, path)
        pic_count += 1


def argv():
    parser = argparse.ArgumentParser(prog='bp2html',
                                     description='把<编排文本>编译为图文html'
                                     )
    parser.add_argument('-i',
                        type=str, help='输入的编排文件',
                        metavar='文件名',
                        required=True,
                        dest='input')
    parser.add_argument('-o',
                        type=str, help='输出的编排文件',
                        metavar='文件名',
                        required=True,
                        dest='output')
    parser.add_argument('-p',
                        type=int, help='分页的页数',
                        metavar='页数',
                        default=0,
                        dest='page')

    args = parser.parse_args()
    return args


def compose_html(title, page, head, pages, htm):
    h1 = '''\
<!DOCTYPE html><html><head>
<meta charset="gb18030">
<title>'''

    h2 = '''\
</title>
<style>
img{max-width:100%;height:auto}
</style>
</head>
'''
    current = ' - 第%d页' % page if page else ''
    html_head = h1 + title + current + h2

    if pages:
        htmls = html_head + '<body bgcolor="#EEEEEE">' \
            + head + pages + '<br>' + htm + '<br><br>' + pages \
            + '<br></body></html>'
    else:
        htmls = html_head + '<body bgcolor="#EEEEEE">' \
            + head + '<br>' + htm \
            + '<br><br></body></html>'

    return htmls


def get_pg_fn(fn, page):
    p = r'^(.*)(\.\w+)$'
    m = re.search(p, fn)
    if m:
        return m.group(1) + ('_%d' % page) + m.group(2)
    else:
        return fn + ('_%d' % page)


def page_html(parg, total, current, fn):
    s = '每页%d图，共%d页 ' % (parg, total)
    for i, _ in enumerate(range(total), 1):
        if i == current:
            s += '<strong>%d</strong> ' % i
        else:
            s += '<a href="%s">%d</a> ' % (get_pg_fn(fn, i), i)
    s += '<br>'

    return s


def split_page(save_dir, htm, head, parg, output):
    p = r'(?:(?=(.*?<img src="[^"]+" />))\1){' + str(parg) + '}'
    p_strip = r'^(?:<br>|\s)*(.*?)(?:<br>|\s)*$'
    end = 0
    lst = []

    # 分割html
    for m in re.finditer(p, htm, re.S):
        begin = m.start()
        end = m.end()
        temp = re.sub(p_strip, r'\1', htm[begin:end], flags=re.S)
        lst.append(temp)

    if end < len(htm) - 1:
        temp = re.sub(p_strip, r'\1', htm[end:], flags=re.S)
        if temp:
            lst.append(temp)

    print('分为%d页' % len(lst))

    # 依次保存
    for i, content in enumerate(lst, 1):
        # 当前文件名
        fn = get_pg_fn(output, i)
        path = os.path.join(save_dir, fn)

        # 上下pages
        pages = page_html(parg, len(lst), i, output)

        # 添加head
        content = compose_html(save_dir, i, head, pages, content)

        with open(path, 'w', encoding='gb18030') as f:
            f.write(content)


def main():
    args = argv()

    try:
        with open(args.input, encoding='gb18030') as f:
            content = f.read()
    except:
        raise Exception('无法读取编排文件: ' + args.input)

    # 提取所有回复
    p_one = (r'(?:^|(?<=\n))\s*<time>[^\n]*\n'
             r'((?:(?!\n<time>).)*?)\n\s*<mark>[^\n]*?(█?)(?:(?=\n)|$)')
    ms = [m for m in re.finditer(p_one, content, re.DOTALL)]
    replys = [m.group(1) for m in ms if m.group(2)]
    print('共%d条回复，摘取%d条回复' % (len(ms), len(replys)))

    # refer
    p_refer = r'(?:^|(?<=\n))<page>网址:\s*([^\s]*)'
    refer = re.search(p_refer, content).group(1)

    # 创建目录
    try:
        p_title = r'(?:^|(?<=\n))<tiezi>标题：\s*([^\n]+)'
        save_dir = re.search(p_title, content).group(1)
    except:
        save_dir = '空标题帖子'

    try:
        os.mkdir(save_dir)
    except:
        pass

    # html主体、下载列表
    htmls, pic_list = process_replys(replys, save_dir)

    # 头信息
    head = get_tieze_head(content)

    if args.page > 0:
        split_page(save_dir, htmls, head, args.page, args.output)
    else:
        htmls = compose_html(save_dir, 0, head, '', htmls)

        path = os.path.join(save_dir, args.output)
        with open(path, 'w', encoding='gb18030') as f:
            f.write(htmls)

    # 下载
    download_pics(refer, pic_list)

    # 发出响声
    if winsound != None:
        try:
            winsound.Beep(400, 320)  # (frequency, duration)
        except:
            pass

    if os.name == 'nt':
        os.system('pause')


main()
