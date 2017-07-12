####界面
1. 定义root界面，界面保持在屏幕的中央
```
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
```
---
*注意*
resizable()：用来指明窗口是否可以固定大小，设置为False，那么该窗口固定大小
withdraw()：让root暂时隐藏
maxsize()：获得屏幕的宽高
geometry()：设置屏幕的尺寸，这里前两个参数代表宽高，后两个参数代表边距
deiconify()：设置完窗口之后进行显示

---
2. 定义main界面
```
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
```
展示界面如图

![ftp.png](http://upload-images.jianshu.io/upload_images/2591003-62ced8cc7c6f7913.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

####函数调用
首先input输入有函数回调get_connect
```
    #对应回调
    #self.input.bind('<Return>', self.get_connect)
    def get_connect(self, event):
            host = self.input.get()
            self.connect(host)
```
---
bind具体用法见http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
这里只需知道该行代码的含义是当用户点击enter键后，会回到self.get_contect函数，并且传递event对象。这里获取input输入的值，然后调用connect函数进行操作

---
```
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
```
---
第一步：判断host合法化
第二步：使用ftplib.FTP函数进行ftp连接，连接失败进行提示
第三步：先不用用户名密码登录，如果失败，使用用户名密码登录，直到正确为止
第四步：获取目录列表，并通过dolistfile进行展示。

---
在用户名密码登录的时候由于没有对应的空间，这里继承了simpledialog.Dialog重写了一个dialog，并重写了body和apply方法
```
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
```
其次连接按钮也可以进行连接
```
    def do_connect(self):
        host = self.input.get()
        self.connect(host)
```
是不是很简单，只需要获得host，然后调用connect进行连接即可
最后是返回上一级
```
    def do_back(self):
        if not self.path:
            return
        self.path.pop()
        curpath = '/'.join(self.path)
        self.f.cwd(curpath)
        self.files = self.f.nlst()
        self.dolistfile()
```
---
这里的self.path存储了用户当前所在目录的路径，比如root/home，将存储为['root','home']，这样可以当做栈来使用，比较方便。pop可以弹出最后一个元素，然后就可以获得上一级的目录，然后显示即可

---
在list中点击一个文件夹就可以进入文件夹并显示所有内容
```
    #对应回调
    #self.list.bind('<Double-1>', self.setDirAndGo)
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
```
---
这里bind绑定的是双击左键
curselection()：获取当前选择的项
通过get可以获得其对应的文本内容
cwd是跳转到该工作目录，如果发生错误，即不能跳转则返回(文件的话就直接返回)
最后将该目录添加到path中，nlst获取工作目录中的所有内容

---
FTP客户端到这里就告一段落了，剩下的在下一篇中进行讲解。希望本文对你有所帮助。