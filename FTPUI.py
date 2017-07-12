import ftplib
import os
import socket
from tkinter import *
from tkinter import messagebox, simpledialog


class LoginDialog(simpledialog.Dialog):
    def body(self, master):
        Label(master, text="用户名:").grid(row=0)
        Label(master, text="密码:").grid(row=1)

        self.e1 = Entry(master)
        self.e2 = Entry(master)

        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        return self.e1

    def apply(self):
        self.name = str(self.e1.get())
        self.pwd = str(self.e2.get())


class FTPUI():

    def setDirAndGo(self, event=None):
        check = self.list.get(self.list.curselection())
        if check:
            try:
                self.f.cwd(check)
                self.path.append(check)
            except ftplib.error_perm:
                return
            self.files = self.f.nlst()
            self.dolistfile()

    def connect(self, host):
        if not host:
            messagebox.showwarning('连接失败', '您输入的FTP地址为空！')
        if host.startswith('ftp:'):
            host = host.replace(r'ftp:', '').replace(r'/','')
            print(host)
        try:
            self.f = ftplib.FTP(host)
        except (socket.error, socket.gaierror) as e:
            messagebox.showwarning('连接失败', '您输入的FTP地址有误！')
            return

        islogin = False
        try:
            self.f.login()
        except (AttributeError, ftplib.error_perm) as e:
            while not islogin:
                try:
                    login = LoginDialog(self.root)
                    self.f.login(login.name, login.pwd)
                    islogin = True
                except ftplib.error_perm:
                    messagebox.showerror('登录失败', '你输入的用户名或密码有误！')

        self.path = []
        rootfile = self.f.pwd()
        self.path.append(rootfile)
        self.files = self.f.nlst(rootfile)
        self.dolistfile()

    def dolistfile(self):
        self.list.delete(0, END)
        for eachFile in self.files:
            eachstring = eachFile.replace(r'/', '')
            self.list.insert(END, eachstring)

    def get_connect(self, event):
        if str(event.char) == '\r':
            host = self.input.get()
            self.connect(host)

    def do_connect(self):
        host = self.input.get()
        self.connect(host)

    def do_back(self):
        if not self.path:
            return
        self.path.pop()
        curpath = '/'.join(self.path)
        self.f.cwd(curpath)
        self.files = self.f.nlst()
        self.dolistfile()

    def rootFrame(self, title):
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.title(title)

        self.root.withdraw()

        self.scnWidth, self.scnHeight = self.root.maxsize()
        self.curWidth = self.scnWidth / 2
        self.curHeight = self.scnHeight * 2 / 3

        tmpcuf = '%dx%d+%d+%d' % (
            self.curWidth, self.curHeight, (self.scnWidth - self.curWidth) / 2, (self.scnHeight - self.curHeight) / 2)
        self.root.geometry(tmpcuf)
        self.root.deiconify()

    def mainFrame(self):
        self.left = Frame(self.root)
        self.leftinput = Frame(self.left)
        self.ftplb = Label(self.leftinput,text='ftp:')
        self.ftplb.pack(side=LEFT)
        self.input = Entry(self.leftinput, width=35)
        self.input.bind('<Return>', self.get_connect)
        self.input.pack(side=LEFT)
        self.conbtn = Button(self.leftinput,text='连接',command=self.do_connect)
        self.conbtn.pack(side=LEFT)
        self.back = Button(self.leftinput,text='返回上一级',command=self.do_back)
        self.back.pack(side=LEFT)
        self.leftinput.pack(side=TOP)

        self.listfm = Frame(self.left)
        self.sclist = Scrollbar(self.listfm)
        self.list = Listbox(self.listfm, width=58, height=30, yscrollcommand=self.sclist.set)
        self.sclist.config(command=self.list.yview)
        self.list.bind('<Double-1>', self.setDirAndGo)
        self.list.pack(side=LEFT)
        self.sclist.pack(side=LEFT, fill=Y)
        self.listfm.pack()
        self.left.pack(side=LEFT)

        self.right = Frame(self.root)
        self.copylist = Button(self.right, text='复制列表')
        self.ziplist = Button(self.right, text='备份')
        self.reglb = Label(self.right, text='匹配规则:')
        self.reg = Entry(self.right)
        self.search = Button(self.right, text='查找文件')
        self.dowload = Button(self.right, text='下载文件')
        self.copylist.pack()
        self.ziplist.pack()
        self.reglb.pack()
        self.reg.pack()
        self.search.pack()
        self.dowload.pack()
        self.right.pack(side=LEFT, fill=Y)

    def __init__(self):
        self.rootFrame('FTP客户端')
        self.mainFrame()


def main():
    FTPUI()
    mainloop()


if __name__ == '__main__':
    main()
