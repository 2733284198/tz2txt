# coding=utf-8

import os
from red import red
import webbrowser
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Radiobutton

import color
color.disable()
import tz2txt
import datamachine
import checkver

#discard_fn = 'auto.txt'
discard_fn = '~discard.txt'
url_use = '复制帖子某页的网址，然后直接按<处理网址>'
        
class Gui(Frame):
    def __init__(self, root):
        super().__init__(root)
        
        # url ============================
        self.url = StringVar()
        self.url.set(url_use)
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
        
        # 使用帮助
        help = Button(self, text='使用帮助', command=self.help_bt)
        help.grid(row=1, column=3)
        
        #================================
        
        # 辅助格式
        l4 = Label(self, text='辅助格式：')
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
        l2 = Label(self, text='下载页数(-1为到末页)：')
        l2.grid(row=3, column=0, columnspan=2, sticky=E)
        
        self.till = StringVar()
        self.till.set('-1')
        entry = Entry(self, textvariable=self.till, width=7)
        entry.grid(row=3, column=2)
        
        # 删除文件
        delfile = Button(self, text='删输出文件', command=self.delfile,
                         fg='#990000')
        delfile.grid(row=3, column=3)
        
        #====================================
        # 输出文件
        l3 = Label(self, text='输出文件：')
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

        if bad or not tz2txt.is_url(u):
            self.url.set('无效网址，网址须以http://或https://开头。')
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
        
        # 执行命令
        self.status['fg'] = '#993300'
        self.status['text'] = '处理中'
        self.update()
        
        # except里return
        try:
            output, discard_output, title, info_list, chinese_ct = \
                tz2txt.auto(u, till, '', 'from_gui', label, from_gui=True)
            if title == None:
                raise Exception('无法完成全自动处理')
        
        except Exception as e:
            print('\n出现异常：', e)
            print('===================================\n')            
            return
        
        else:
            # 显示标题
            title = red.sub(r'[\U00010000-\U0010FFFF]', r'', title)
            title = title.strip()
            self.url.set(title)
        
        finally:
            self.status['fg'] = 'blue'
            self.status['text'] = '待机'
                    
        # 输出文件名
        if self.rename.get():
            output_fn = title + '.txt'
        else:
            output_fn = self.output.get().strip()
        
        # 合法文件名
        output_fn = red.sub(r'[\\/:*?"<>|]', r'', output_fn)
        if output_fn == '.txt':
            output_fn = '楼主.txt'
        
        # 输出内容
        text = output.getvalue()
        output.close()
            
        # 覆盖判断：文件已存在 and 输出有内容 and (强制覆盖 or 选择覆盖)
        if os.path.isfile(output_fn) and \
           text and \
           (self.override.get() == 1 or \
            messagebox.askyesno('输出文件已存在', '是否覆盖？\n%s' % output_fn)
            ):
            # 删除已有目标
            try:
                os.remove(output_fn)
            except:
                pass
        
        # 写入output
        if not os.path.isfile(output_fn) and text:
            try:
                with open(output_fn, 'w', 
                          encoding='gb18030', errors='replace') as f:
                    f.write(text)
                print('\n已保存为：', output_fn)
            except Exception as e:
                print('\n保存文件时出现异常', e)
        
            # 显示信息 
            size2 = os.path.getsize(output_fn)
            size2 = format(size2, ',')
            chinese_ct = format(chinese_ct, ',')
            print('输出文件{0}字节，约{1}个汉字。'.format(
                                                        size2,
                                                        chinese_ct)
                  )
                
        # 写入discard
        if discard_output != None:
            try:
                text = discard_output.getvalue()
                discard_output.close()
                
                if text:
                    with open(discard_fn, 'w', 
                              encoding='gb18030', errors='replace') as f:
                        f.write(text)
            except Exception as e:
                print('\n保存文件时出现异常', e)

        print()
        for line in info_list:
            if line.startswith('下载时间：'):
                break
            datamachine.save_print(line.rstrip('\n'))
        print('===================================\n')

        
    def delfile(self):
        try:
            output = self.output.get().strip()
            os.remove(output)
        except:
            pass
        
        try:
            os.remove(discard_fn)
        except:
            pass
        
        self.url.set(url_use)
        
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
            if newver > tz2txt.tz2txt_date:
                print('发现新版本:', newver)
                if messagebox.askyesno('发现新版本', 
                        '最新版本：%s\n是否用浏览器打开下载网址？' % newver):
                    try:
                        webbrowser.open_new_tab(download_url)
                    except:
                        print('无法用浏览器打开下载网址：', download_url)
            elif newver != tz2txt.tz2txt_date:
                print('当前版本比网盘版本(%s)新' % newver)
            else:
                print('检查完毕，没有发现新版本')
            print()
        
        self.status['fg'] = 'blue'
        self.status['text'] = '待机'
        
    def help_bt(self):
        url = 'http://www.cnblogs.com/animalize/p/4770397.html'
        try:
            webbrowser.open_new_tab(url)
        except:
            print('无法用浏览器打开使用帮助，网址：', url)
        
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
    
    root.resizable(False, False)
    root.mainloop()

if __name__ == '__main__':
    main()