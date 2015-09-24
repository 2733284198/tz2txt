# coding=utf-8

import os
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Radiobutton

import color
color.disable()
import tz2txt
import datamachine
import checkver

output = 'auto.txt'
discard = '~discard.txt'
        
class Gui(Frame):
    def __init__(self, root):
        super().__init__(root)
        
        # url
        self.url = StringVar()
        self.url.set('复制某页的网址，直接按<处理网址>')
        entry = Entry(self, textvariable=self.url,
                      bg='#666699', fg='#FFFFFF')
        entry.grid(row=0, column=0, columnspan=3, sticky=W+E)
        
        # 粘贴并打开
        self.paste_do = Button(self, text='处理网址', command=self.doit,
                               bg='#cc9933')
        self.paste_do.grid(row=1, column=0)
        
        # 覆盖
        self.override = IntVar()
        self.override.set(0)
        cb = Checkbutton(self,
                         variable=self.override,
                         text = '覆盖文件')
        cb.grid(row=1, column=1)
        
        # 状态
        self.status = Label(self, text='待机', fg='blue')
        self.status.grid(row=1, column=2)
        
        # 辅助格式
        self.assist = IntVar()
        self.assist.set(2)
        
        r1 = Radiobutton(self, text='无辅助',
                         variable=self.assist, value=1)
        r1.grid(row=2, column=0)
        
        r2 = Radiobutton(self, text='页码模式',
                         variable=self.assist, value=2)
        r2.grid(row=2, column=1)
        
        self.r3 = Radiobutton(self, text='楼层模式',
                         variable=self.assist, value=3)
        self.r3.grid(row=2, column=2)
        
        # 末页
        l2 = Label(self, text='下载页数(-1为到末页):')
        l2.grid(row=3, column=0, columnspan=2)
        
        self.till = StringVar()
        self.till.set('-1')
        entry = Entry(self, textvariable=self.till, width=7)
        entry.grid(row=3, column=2)
                
        # 重命名
        rename_bt = Button(self, text='自动重命名', command=self.rncmd)
        rename_bt.grid(row=4, column=0)
        
        # 检查更新
        update_bt = Button(self, text='检查更新', command=self.checkver)
        update_bt.grid(row=4, column=1)
        
        # 删除文件
        delfile = Button(self, text='删auto.txt', command=self.delfile,
                         fg='#990000')
        delfile.grid(row=4, column=2)
        
        # self
        self.pack()
        
        self.fixrb()
        
    def fixrb(self):
        # fix radiobutton draw
        self.r3.focus_force()
        self.paste_do.focus_force()
    
    def doit(self):
        u = self.master.clipboard_get().strip()
        if not tz2txt.is_url(u, silence=True):
            self.url.set('无效网址')
            return
        self.url.set(u)
        
        # 覆盖？
        override = self.override.get()
        if override == 0 and os.path.isfile(output):
            answer = messagebox.askyesno('输出文件已存在', 
                                         '是否覆盖？')
            if answer == False:
                return
        
        # 辅助模式
        assist = self.assist.get()
        if assist == 1:
            label = ''
        elif assist == 2:
            label = 'page'
        elif assist == 3:
            label = 'floor'
            
        # 末页
        till = self.till.get().strip()
        try:
            till = int(till)
        except:
            till = -1
        
        # 执行命令
        self.status['fg'] = '#993300'
        self.status['text'] = '处理中'
        self.update()
        try:
            info_list = tz2txt.auto(u, till,
                                     output, discard,
                                     label)
        except Exception as e:
            print('出现异常：', e)
            info_list = None

        self.status['fg'] = 'blue'
        self.status['text'] = '待机'
        if info_list:
            print()
            for line in info_list:
                if line.startswith('下载时间：'):
                    continue
                datamachine.save_print(line.rstrip('\n'))
            print('===================================\n')
        
    def delfile(self):
        try:
            os.remove(output)
        except:
            pass
        
        try:
            os.remove(discard)
        except:
            pass
        
    def checkver(self):
        self.status['fg'] = '#993300'
        self.status['text'] = '处理中'
        self.update()
        
        print('当前版本:', tz2txt.tz2txt_date)
        
        try:
            newver, download_url = checkver.check()
        except Exception as e:
            print('出现异常：', e)
        else:
            if tz2txt.tz2txt_date != newver:
                print('发现新版本:', newver)
            else:
                print('检查完毕，没有发现新版本')
            print()
        
        self.status['fg'] = 'blue'
        self.status['text'] = '待机'
        
    def rncmd(self):
        try:
            title = ''
            with open(output, encoding='gb18030') as f:
                for i, line in enumerate(f):
                    if i > 1:
                        break
                    if line.startswith('标题：'):
                        title = line[len('标题：'):].strip()
                        
            if title:
                os.renames(output, title+'.txt')
                print('重命名为：', title+'.txt')
            else:
                print('无法提取标题')
        except:
            pass
        
def main():
    root = Tk()
    root.wm_title('tz2txt图形界面')
    
    gui = Gui(root)
    
    # center on screen
    root.update()
    w = gui.winfo_reqwidth()
    h = gui.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    print('程序版本: %s\n' % tz2txt.tz2txt_date)
    
    root.mainloop()

if __name__ == '__main__':
    main()