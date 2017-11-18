#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from time import strftime,gmtime
import smtplib,mimetypes
from smtplib import SMTP, SMTP_SSL
import requests,re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import random
from pyquery import PyQuery

user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]


mail_host="smtp.163.com"
mail_user="xxx@163.com"
mail_pass="password"
mail_port="25"

date = strftime("%Y%m%d", gmtime())
# Time = str(time.time())
mailto_list = ["xxxx@163.com"]
subject = (date + "-" + "tingyu test")
content = "测试文件"

#之前写过的代码
#返回格式是一段字符串： 第一行：内容 ， 第二行：作者
def get_jiandan():
    url = "https://jandan.net/duan"
    content = requests.get(url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(content)
    max_page = list(py_content('.current-comment-page').items())[0].text()
    max_page = int(re.search("\d+",max_page).group())

    random_page = random.choice(range(max_page-20,max_page))
    random_url = "https://jandan.net/duan/page-{page}#comments".format(page=random_page)
    content = requests.get(random_url,headers={"User-Agent":random.choice(user_agent_list)}).content
    py_content = PyQuery(content)
    all_comments = list(py_content('.commentlist > li > div > div').items())
    signal_comment = random.choice(all_comments)
    author = signal_comment('.author > strong').text()
    text = signal_comment('.text > p').text()
    info = []
    info.append(author.encode('utf8'))
    info.append(text.encode('utf8'))
    res = info[1] + "\n\nby " + info[0]
    return res

#接收人是一个list
def send_mail(to_list,sub,content):
    me=mail_user

    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)

    # 邮件内容
    txt = MIMEText(content,"plain",'utf-8')
    #msg = MIMEText(content, format, 'utf-8')  #解决中文乱码 ， 其中的format指的是你设定的文本格式，一般为'plain'
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"
    msg.attach(txt)     #attach表示附加东西，下面的附件也是

    # 添加附件
    fileName = str("test.txt")
    #ctype一般为 text/plain , encodeing 为 None
    ctype, encoding = mimetypes.guess_type(fileName)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)     #这里还是用的subtype (为 'plain')
    # 将文件中的内容写入到att1中，并附加信息发送
    att1 = MIMEImage((lambda f: (f.read(), f.close()))(open(fileName, 'rb'))[0], _subtype = subtype)
    att1.add_header('Content-Disposition', 'attachment', filename = fileName)
    msg.attach(att1)

    try:
        s = smtplib.SMTP_SSL()
        s.connect(mail_host)
        #设置服务器，用户名、口令以及加密端口
        s.login(mail_user,mail_pass)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    if send_mail(mailto_list,subject,get_jiandan()):
        print "发送成功"
    else:
        print "发送失败"






