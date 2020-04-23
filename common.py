# -*- coding:utf-8 -*-
#author:liaoren
#time:2020/04/23
#description:This file packages the common functions of python into objects, which is convenient to call  

#################### send Email
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr,formataddr
import smtplib,socket

class Email(object):
    def __init__(self,addr,passwd,server,port):
        self.__FromAddr = addr
        self.__FromName = socket.gethostname()
        self.__Passwd = passwd
        self.__SmptServer = server
        self.__SmptPort = port

    def Send(self,msg,subject,ToName,*Addr):
        msg = MIMEText(msg, "plain", "utf-8")
        msg["From"] = self.__FormatAddr("%s<%s>" %(self.__FromName,self.__FromAddr))
        msg["To"] = self.__FormatAddr("%s<%s>" %(ToName,str(Addr)[1:-1]))
        msg["Subject"] = Header(subject, "utf-8").encode()
        server = smtplib.SMTP(self.__SmptServer, self.__SmptPort)
        server.starttls()
        server.login(self.__FromAddr, self.__Passwd)
        server.sendmail(self.__FromAddr, list(Addr), msg.as_string())
        server.quit()

    def SetInfo(self,**kwargs):
        for i in kwargs.keys():
            if i == "FromAddr":
                self.__FromAddr = kwargs["FromAddr"]
            elif i == "Passwd":
                self.__Passwd = kwargs["Passwd"]
            elif i == "SmptServer":
                self.__SmptServer = kwargs["SmptServer"]
            elif i == "SmptPort":
                self.__SmptPort = kwargs["SmptPort"]
            else:
                pass
    @staticmethod
    def __FormatAddr(s):
        name,addr = parseaddr(s)
        return formataddr((Header(name,"utf-8").encode(),addr))

#################### http request with different methods
from urllib import request, error, parse
import http.cookiejar
class MyRequest(object):
    def __init__(self):
        self.Resp = 0
        cookie = http.cookiejar.MozillaCookieJar()
        NewOpener = request.build_opener(request.HTTPCookieProcessor(cookie))
        request.install_opener(NewOpener)  # 安装NewOpener实例作为默认全局启动器

    def GetResp(self,Url, Data={}, Headers={}, Method=0):
        try:
            if Method == 0:  # get请求
                Data = parse.urlencode(Data)
                req = request.Request(url='%s%s%s' % (Url, '?', Data), headers=Headers)
            elif Method ==1:  # post请求（content-type为其它，如form-data等）
                Data = (parse.urlencode(Data)).encode('utf-8')
                req = request.Request(Url, data=Data, headers=Headers)
            elif Method == 2: # Post请求（content-type为application/json）
                Data = json.dumps(Data).encode('utf-8')
                req = request.Request(Url, data=Data, headers=Headers)
            else:
                pass
            self.Resp = request.urlopen(req)  # 发出请求
        except error.URLError as e:
            print("Error happened!%s"%e)
            self.Resp = 0

    def GetRespInfo(self,p = True):
        if isinstance(web.Resp,http.client.HTTPResponse):
            if p:
                for k,v in self.Resp.getheaders():
                    print("%s:%s"%(k,v))
            else:
                return self.Resp.getheaders()

#################### manage process by python file itself
import sys,os,signal
class ProcessManage(object):
    def __init__(self,ExitHandle=None):
        if hasattr(ExitHandle,"__call__"):
            self.__ExitFunc = ExitHandle    #初始化该对象时必须传入一个函数作为参数，该函数是程序结束时需要处理的事务
        else:
            print("process manage program  failed to start!please enter the ExitHandle!")
            sys.exit(0)
        signal.signal(signal.SIGTERM,self.__Exit)
        ########## 处理参数，实现通过一个代码文件控制程序的启动停止重启的功能 ##########
        if len(sys.argv)>1:
            cmd = "ps -aux | grep python | awk '{for(i=1;i<=NF;i++)if($i==\"%s\")print $2;}'"%sys.argv[0]  #’sys.arg[0]‘即为下文的‘该文件’
            ps_pid = [int(x) for x in ((os.popen(cmd)).read()).split('\n') if x!='']  #使用ps、ps、awk命令找出所有通过该文件启动的进程的pid
            my_pid = os.getpid()
            if sys.argv[1] == "start":  #启动命令，需要检查是否有通过该文件启动的其他进程，有则本进程自动结束，没有则该进程继续运行
                for i in ps_pid:
                    if i != my_pid:
                        print("an instance process has ben started through this file,and the process will exit automatically.")
                        sys.exit(0)
            elif sys.argv[1] == "stop":  #关闭命令，关闭所有通过该文件启动的进程，本进程自动结束
                for i in ps_pid:
                    if i != my_pid:
                        os.kill(i,signal.SIGTERM)
                print("other processes started through this file have been closed,and the process will exit automatically.")
                sys.exit(0)
            elif sys.argv[1] == "restart":  #重启命令，关闭本进程以外的其它通过该文件启动的进程，本进程继续运行
                for i in ps_pid:
                    if i != my_pid:
                        os.kill(i,signal.SIGTERM)
                print("other processes started through this file have been closed,and the process will start automatically.")
            else:  #命令书写错误
                print("the parameters is false,please enter the correct parameters(start,stop,restart).")
                sys.exit(0)
        else:  #没有输入命令
            print("""please enter parameters!
                       1. start    start the program.
                       2. stop     stop the program,kill all processes.
                       3. restart  restart the program,kill all other processes.""")
            sys.exit(0)
    def __Exit(self,signum,handle):
        if signum == signal.SIGTERM:
            self.__ExitFunc()
            sys.exit(0)


#################### offer the api of mysql
import mysql.connector
class MySQL(object):
    def __init__(self,host="localhost",user="liaoren",passwd="123456",db="bilibili_data",auth="mysql_native_password"):
        self.__Host = host
        self.__User = user
        self.__Passwd = passwd
        self.__Auth = auth
        self.__DB = db
    ########## 将数据存入数据库 ##########
    def Modify(self,*cmd):
        con = mysql.connector.connect(host=self.__Host,user=self.__User,password=self.__Passwd,
                                      auth_plugin=self.__Auth,database=self.__DB)
        curson = con.cursor()
        try:
            for i in cmd:
                curson.execute(i)
                con.commit()            #对数据库进行增删改必须要使用该函数
        except BaseException as e:
            print("Error happened in modifying mysql！%s"%e)
            curson.close()
            con.close()
            return 0
        curson.close()
        con.close()
        return 1
    ########## 查询数据库数据 ##########
    def Query(self,cmd):
        con = mysql.connector.connect(host=self.__Host,user=self.__User,password=self.__Passwd,
                                      auth_plugin=self.__Auth,database=self.__DB)
        curson = con.cursor(buffered=True)
        try:
            curson.execute(cmd)
            result = curson.fetchall()
        except BaseException as e:
            logging.error("Error happened in querying mysql！%s"%e)
            curson.close()
            con.close()
            return 0
        curson.close()
        con.close()
        return result
