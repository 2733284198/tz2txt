import re
import os
import sys
import binascii

try:
    import winsound
except:
    winsound = None

from fetcher import *

p_one = (r'(?:^|(?<=\n))\s*<time>[^\n]*\n'
         r'((?:(?!\n<time>).)*?)\n\s*<mark>[^\n]*?(█?)(?:(?=\n)|$)')
p_refer = r'(?:^|(?<=\n))<page>网址:\s*([^\s]*)'
p_img = r'\[img\s*\d*\](.*?)\[/img\]'
p_title = r'(?:^|(?<=\n))<tiezi>标题：\s*([^\n]+)'

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
            r'起始网址：<a href="\5" target=_blank>\5</a><br><br>'
            )

fetcher = None
save_dir = None
pic_list = []

pic_count = 1


def get_fn(url):
    global pic_count

    crc = binascii.crc32(url.encode('utf-8'))
    crc = '{:08x}'.format(crc)

    m = re.search(r'^.*(\.\w+)$', url)
    if m:
        fn = str(pic_count) + '_' + crc + m.group(1)
    else:
        fn = str(pic_count) + '_' + crc + '.jpg'

    pic_count += 1

    return fn


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
        fn = get_fn(url)

        global save_dir
        path = os.path.join(save_dir, fn)

        global pic_list
        pic_list.append((path, url))

        # 替换html
        ret += '<img src="%s" />' % fn

    ret += s[last:]
    return ret


def download_pics():
    pic_count = 1
    pic_all = len(pic_list)

    for path, url in pic_list:
        if not os.path.exists(path):
            print('(%d/%d)保存图片:' % (pic_count, pic_all), url)

            fetcher.save_file(url, path)
        pic_count += 1


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
    ms = [m for m in re.finditer(p_one, content, re.DOTALL)]
    replys = [m.group(1) for m in ms if m.group(2)]
    print('共%d条回复，摘取%d条回复' % (len(ms), len(replys)))

    refer = re.search(p_refer, content).group(1)

    # 下载器
    fetcher_info = FetcherInfo()
    fetcher_info.referer = refer
    global fetcher
    fetcher = Fetcher(fetcher_info)

    # 创建目录
    global save_dir
    save_dir = re.search(p_title, content).group(1)
    try:
        os.mkdir(save_dir)
    except:
        pass

    htmls = [process_reply(reply) for reply in replys]
    htmls = '<br><br>'.join(htmls)
    htmls = htmls.replace('\n', '<br>\n')

    m = re.search(p_head, content)
    if m:
        head = m.expand(sub_head)
    else:
        head = ''

    htmls = '<!DOCTYPE html><html><body bgcolor="#EEEEEE">' \
        + head + htmls \
        + '<br><br></body></html>'

    path = os.path.join(save_dir, args[1])
    with open(path, 'w', encoding='gb18030') as f:
        f.write(htmls)

    # 下载
    download_pics()

    # 发出响声
    if winsound != None:
        try:
            winsound.Beep(400, 320)  # (frequency, duration)
        except:
            pass

    if os.name == 'nt':
        os.system('pause')


main()
