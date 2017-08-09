import re
import os
import sys

from fetcher import *

p_one = r'(?:^|(?<=\n))\s*<time>[^\n]*\n(.*?)\n\s*<mark>[^\n]*█'
p_refer = r'(?:^|(?<=\n))<page>网址:\s*([^\s]*)'
p_img = r'\[img\s*\d*\](.*?)\[/img\]'
p_fn = r'^.*/(.*)$'
p_title = r'(?:^|(?<=\n))<tiezi>标题：\s*([^\n]+)'

fetcher = None
dir = None

pic_all = 0
pic_count = 1


def process_reply(s):
    ret = ''
    last = 0

    while True:
        m = re.search(p_img, s[last:], re.I)
        if m is None:
            break

        ret += s[last:last + m.start(0)]
        last = last + m.end(0)

        # 提取图片url
        url = m.group(1)

        # 保存文件
        fn = re.search(p_fn, url).group(1)

        global dir
        path = os.path.join(dir, fn)

        if not os.path.exists(path):
            global pic_count, pic_all
            print('(%d/%d)保存图片:' % (pic_count, pic_all), url)

            fetcher.save_file(url, path)
        pic_count += 1

        # 替换html
        ret += '<img src="%s" />' % fn

    ret += s[last:]
    return ret


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print('用法：bp2html.py <bp.txt> <out.html>')
        print('尖括号内为两个参数，前者为编排文件，后者为输出文件')
        sys.exit()

    try:
        with open(args[0], encoding='gb18030') as f:
            content = f.read()
    except:
        raise Exception('无法读取编排文件: ' + args[0])

    # 提取
    replys = [m.group(1) for m in re.finditer(p_one, content, re.DOTALL)]
    refer = re.search(p_refer, content).group(1)

    global pic_all
    pic_all = len(re.findall(p_img, content))

    # 下载器
    fetcher_info = FetcherInfo()
    fetcher_info.referer = refer
    global fetcher
    fetcher = Fetcher(fetcher_info)

    # 目录
    global dir
    dir = re.search(p_title, content).group(1)
    try:
        os.mkdir(dir)
    except:
        pass

    htmls = [process_reply(reply) for reply in replys]
    htmls = '<br>'.join(htmls)
    htmls = htmls.replace('\n', '<br>\n')
    htmls += '<br><br>'

    path = os.path.join(dir, args[1])
    with open(path, 'w', encoding='gb18030') as f:
        f.write(htmls)


main()
