# coding=utf-8

import os
import tempfile
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Radiobutton

import color
color.disable()
import tz2txt
import datamachine
import checkver

#output = 'auto.txt'
discard = '~discard.txt'
        
class Gui(Frame):
    def __init__(self, root):
        super().__init__(root)
        
        # url ============================
        self.url = StringVar()
        self.url.set('复制帖子某页的网址，然后直接按<处理网址>')
        entry = Entry(self, textvariable=self.url,
                      bg='#666699', fg='#FFFFFF')
        entry.grid(row=0, column=0, columnspan=4, sticky=W+E)
        
        #==================================
        # 粘贴并打开
        self.paste_do = Button(self, text='处理网址', command=self.doit,
                               bg='#cc9933')
        self.paste_do.grid(row=1, column=0)
    
        # 状态
        self.status = Label(self, text='待机', fg='blue')
        self.status.grid(row=1, column=1)
        
        # 检查更新
        update_bt = Button(self, text='检测新版本', command=self.checkver)
        update_bt.grid(row=1, column=2)
        
        # 删除文件
        delfile = Button(self, text='删输出文件', command=self.delfile,
                         fg='#990000')
        delfile.grid(row=1, column=3)
        
        #================================
        
        # 辅助格式
        l4 = Label(self, text='辅助格式:')
        l4.grid(row=2, column=0)
        
        self.assist = IntVar()
        self.assist.set(2)
        
        r1 = Radiobutton(self, text='无辅助',
                         variable=self.assist, value=1)
        r1.grid(row=2, column=1)
        
        r2 = Radiobutton(self, text='页码模式',
                         variable=self.assist, value=2)
        r2.grid(row=2, column=2)
        
        self.r3 = Radiobutton(self, text='楼层模式',
                         variable=self.assist, value=3)
        self.r3.grid(row=2, column=3)
        
        # 末页
        l2 = Label(self, text='下载页数(-1为到末页):')
        l2.grid(row=3, column=0, columnspan=2, sticky=E)
        
        self.till = StringVar()
        self.till.set('-1')
        entry = Entry(self, textvariable=self.till, width=7)
        entry.grid(row=3, column=2)
        
        #====================================
        # 输出文件
        l3 = Label(self, text='输出文件:')
        l3.grid(row=4, column=0)
        
        self.output = StringVar()
        self.output.set('auto.txt')
        self.e_out = Entry(self, textvariable=self.output, width=10)
        self.e_out.grid(row=4, column=1)

        # 重命名
        self.rename = IntVar()
        self.rename.set(0)
        def callCheckbutton():
            v = self.rename.get()
            if v:
                self.e_out.config(state='disabled')
            else:
                self.e_out.config(state='normal')
            
        cb = Checkbutton(self,
                         variable=self.rename,
                         text='自动重命名',
                         command=callCheckbutton)
        cb.grid(row=4, column=2)
        
        # 覆盖
        self.override = IntVar()
        self.override.set(0)
        cb = Checkbutton(self,
                         variable=self.override,
                         text = '覆盖已有文件')
        cb.grid(row=4, column=3)
        
        #====================================
        
        # self
        self.pack()
        
        self.fixrb()
        
    def fixrb(self):
        # fix radiobutton draw
        self.r3.focus_force()
        self.paste_do.focus_force()
    
    def doit(self):
        # 获取、显示网址
        try:
            u = self.master.clipboard_get().strip()
        except:
            bad = True
            u = ''
        else:
            bad = False

        if bad or not tz2txt.is_url(u, silence=True):
            self.url.set('无效网址')
            return
        self.url.set(u)
        
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
            
        # 得到临时文件名
        try:
            curdir = os.getcwd()
            f = tempfile.NamedTemporaryFile(delete=False,dir=curdir)
            f_name = f.name
            f.close()
        except:
            print('无法创建临时文件')
            return
        
        # 执行命令
        self.status['fg'] = '#993300'
        self.status['text'] = '处理中'
        self.update()
        
        title = '没有找到标题'
        try:
            info_list = tz2txt.auto(u, till,
                                     f_name, discard,
                                     label)
        except Exception as e:
            print('出现异常：', e)
            info_list = None
            return
        else:
            # 提取标题
            if self.rename.get():
                for line in info_list:
                    if line.startswith('标题：'):
                        title = line[len('标题：'):].strip()
                        break
        finally:
            self.status['fg'] = 'blue'
            self.status['text'] = '待机'
                    
        # 输出文件名
        if self.rename.get():
            output = title + '.txt'
        else:
            output = self.output.get().strip()
            
        # 覆盖？
        ok = False
        if (not os.path.isfile(output) or \
            self.override.get() == 1 or \
            messagebox.askyesno('输出文件已存在', 
                                '是否覆盖？\n%s' % output)) and \
            os.path.getsize(f_name) > 0:
                # 删除已有目标
                try:
                    os.remove(output)
                except:
                    pass
                
                # 重命名
                try:
                    os.renames(f_name, output)
                    print('\n重命名为：', output)
                except Exception as e:
                    print('\n重命名时出现异常', e)
                else:
                    ok = True
        else:
            # 删除临时文件
            try:
                os.remove(f_name)
            except:
                pass

        if ok and info_list:
            print()
            for line in info_list:
                if line.startswith('下载时间：'):
                    continue
                datamachine.save_print(line.rstrip('\n'))
            print('===================================\n')
        
    def delfile(self):
        try:
            output = self.output.get().strip()
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
        
def main():
    root = Tk()
    root.wm_title('tz2txt - 全自动处理')
    
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