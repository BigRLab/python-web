# -*- coding: utf-8 -*-
from django_extensions.management.jobs import HourlyJob
from blog.models import Property_operation_history
from blog.models import Property_content
import blog.ansible_tomcat_deploy
import blog.ansible_property as ansible_property
from blog.ansible_api import MyRunner
from email.mime.text import MIMEText
from email.header import Header
import time
import tempfile
import json
import os,sys
import shutil
import smtplib

class Job(HourlyJob):
    help = "My property info write job."

    #def execute(self):
    #    # executing empty sample job
    #    pass

    def execute(self):
        print "cron pool write"
        property_xen_all = Property_content.objects.values("xen_name")
        property_xen_name = []
        property_xen_list = []
        for i in property_xen_all:
            if i["xen_name"] not in property_xen_name:
                property_xen_list.append(i["xen_name"])
                property_xen_name.append(i["xen_name"])
        property_xen_ip = []
        for i in property_xen_list:
            ip_result = Property_content.objects.filter(xen_name=i).values("xen_ip").first()
            property_xen_ip.append(ip_result["xen_ip"])
        baseDir = os.path.dirname(os.path.abspath(__name__));
        hosts_filedir = os.path.join(baseDir,'upload', 'property_tempfile', time.strftime('%Y'), time.strftime('%m'), time.strftime('%d'));
        file_dir="./upload/property_tempfile"
        if not os.path.exists(hosts_filedir):
            os.makedirs(hosts_filedir)
        print "+++" * 200
        print property_xen_ip
        print "+++" * 200
        for ip_name in property_xen_ip:
            addr=ip_name.strip().split('.')
            if len(addr) != 4:
                continue
            property_hosts_list=tempfile.NamedTemporaryFile(prefix=ip_name, suffix="hosts",dir=file_dir)
            property_hosts_list.writelines(['[pool-ip]\n', '%s ansible_ssh_user=username ansible_ssh_pass=passwd\n' % ip_name])
            property_hosts_list.seek(0)
            property_ip_file = ansible_property.run_adhoc(property_hosts_list.name, "script", "./blog/pool_info.sh")
            property_copy = ansible_property.run_adhoc(property_hosts_list.name, "synchronize", "mode=pull src=/tmp/%s dest=%s" % (ip_name, hosts_filedir))
            property_hosts_list.close()
            if property_copy == 0:
                hosts_file_name = hosts_filedir+"/"+ip_name
                property_info = property_write_db(hosts_file_name)
        #print "cron pool yes"
        #property_suf_mail()
        #print "sendmail yes"
    
def property_write_db(hosts_file_name):
    f = open(hosts_file_name, "r")
    line = f.readlines()
    host_list = []
    for i in line:
        host_list.append(i.strip())
    f.close()
    ##########
    pool_name=host_list[0]
    host_list = host_list[1:]
    xe_name = ""
    dic_name = {}
    for i in host_list:
        if i[:2] == "xe":
            host_name = ""
            xe_name = i
            dic_name[xe_name] = host_name
        else:
            host_name = i
            if dic_name[xe_name] == "":
                dic_name[xe_name] = host_name
            else:
                list_name = dic_name[xe_name]
                dic_name[xe_name] = list_name+"#####"+host_name
    #########
    dic_key = dic_name.keys()
    ip_failed=[]
    for xe_ip in dic_key:
        if dic_name[xe_ip] == "":
            continue
        else:
            for host_ip in  dic_name[xe_ip].split("#####"):
                try:
                    ip_name = host_ip.split("-",1)[0]
                    ip_info = host_ip.split("-",1)[1]
                    host_info = ip_info.split('===')
                    ip_remark=host_info[0]
                    ip_cpu=host_info[1]
                    ip_memory=str(round(float(host_info[2])/1024/1024/1024))
                    ip_disk_all=host_info[3].split()
                    ip_disk=""
                    for i in ip_disk_all:
                        ip_disk=ip_disk+str(int(round(float(i)/1024/1024/1024)))+" "

                    ip_exist = Property_content.objects.filter(ip_name=ip_name)
                    if len(ip_exist) == 0:
                        property_db_write(Property_content(), ip_name=ip_name, ip_remark=ip_remark, xen_name=pool_name, xen_ip=xe_ip[3:], host_cpu=ip_cpu, host_memory=ip_memory, host_disk=ip_disk, server_model="虚拟机")
                except IndexError:
                    ip_name = host_ip.split("===",1)[0]
                    ip_failed.append(ip_name)
                except ValueError:
                    ip_name = host_ip.split("===",1)[0]
                    ip_failed.append(ip_name)
    if len(ip_failed) != 0:
        property_send_mail(ip_failed)
    else:
        print "not accord with host_name"
    return "0"

def property_send_mail(ip_name):
    property_send_info = "以下IP信息在xenserver中命名规范不符合标准，标准为：命名不能有空格，并且以ip开头加上-用处，如：(172.30.1.100-nginx)，赶紧去补，不然每天都发邮件，烦死你！！！\n\n"
    for i in ip_name:
        property_send_info = property_send_info + "  ---  "  + i + "\n"
    print property_send_info
    sender = 'ligh@test.com.cn'
    receivers = ['ligh`@test.com.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    mail_msg = """
    <p>%s</p>
    """  % (property_send_info)
    message = MIMEText('%s' % property_send_info, 'plain', 'utf-8')
    message['From'] = Header("cmdb")
    message['To'] =  Header("ligh")

    subject = '命名不规范IP'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

def property_suf_mail():
    property_send_info = "已经更新资产表信息\n\n"
    print property_send_info
    sender = 'cmdb@test.com.cn'
    receivers = ['ligh@test.com.cn']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    mail_msg = """
    <p>%s</p>
    """  % (property_send_info)
    message = MIMEText('%s' % property_send_info, 'plain', 'utf-8')
    message['From'] = Header("cmdb")
    message['To'] =  Header("ligh")

    subject = '资产表更新'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

def property_db_write(table, team_name=None, domain_name=None, ip_name=None, ip_remark=None, app_name=None, system_name=None, principal_name=None, xen_name=None, room_name=None, xen_ip=None, host_cpu=None, host_memory=None, host_disk=None, server_model=None):
    print "DB write"
    print  team_name, domain_name, ip_name, ip_remark, app_name, system_name, principal_name, xen_name, room_name, xen_ip
    blog = table
    blog.team_name = team_name
    blog.domain_name = domain_name
    blog.ip_name = ip_name
    blog.ip_remark = ip_remark
    blog.app_name = app_name
    blog.system_name = system_name
    blog.principal_name = principal_name
    blog.xen_name = xen_name
    blog.room_name = room_name
    blog.xen_ip = xen_ip
    blog.host_cpu = host_cpu
    blog.host_memory = host_memory
    blog.host_disk = host_disk
    blog.server_model = server_model
    blog.save()
    return "0"
