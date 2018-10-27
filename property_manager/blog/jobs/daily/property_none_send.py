# -*- coding: utf-8 -*-
from django_extensions.management.jobs import HourlyJob
from blog.models import Property_operation_history
from blog.models import Property_content
import blog.ansible_tomcat_deploy
import blog.ansible_property as ansible_property
from blog.ansible_api import MyRunner
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import time
import tempfile
import json
import os
import shutil

class Job(HourlyJob):
    help = "My property info none send mail job."

    #def execute(self):
    #    # executing empty sample job
    #    pass

    def execute(self):
        #property_none_info = Property_content.objects.filter(team_name=None, domain_name=None, app_name=None, system_name=None, principal_name=None, room_name=None).values("ip_name")
        property_none_team = Property_content.objects.filter(team_name=None).values("ip_name")
        property_none_domain = Property_content.objects.filter(domain_name=None).values("ip_name")
        property_none_app = Property_content.objects.filter(app_name=None).values("ip_name")
        property_none_system = Property_content.objects.filter(system_name=None).values("ip_name")
        property_none_cpu = Property_content.objects.filter(host_cpu=None).values("ip_name")
        property_none_memory = Property_content.objects.filter(host_memory=None).values("ip_name")
        property_none_disk = Property_content.objects.filter(host_disk=None).values("ip_name")
        property_none_model = Property_content.objects.filter(server_model=None).values("ip_name")
        property_none_principal = Property_content.objects.filter(principal_name=None).values("ip_name")
        property_none_room = Property_content.objects.filter(room_name=None).values("ip_name")
        property_none_all = []
        for i_dic in property_none_team, property_none_domain, property_none_app, property_none_system, property_none_cpu, property_none_memory, property_none_disk, property_none_model, property_none_principal, property_none_room:
            for i in i_dic:
                property_none_all.append(i)
        
        property_none_info = []
        for i in property_none_all:
            if i not in property_none_info:
                property_none_info.append(i)
        
        property_ip_name = []
        for i in property_none_info:
            property_ip_name.append(i["ip_name"].encode('utf-8'))
        
        print property_ip_name
        property_send_info = "以下是资产信息不全的IP地址，赶紧去补，不然每天都发邮件，烦死你！！！\n\n"
        for i in property_ip_name:
            property_send_info = property_send_info + "  ---  "  + i + "\n"
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
    
        subject = '资产信息不全IP'
        message['Subject'] = Header(subject, 'utf-8')
    
        try:
            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message.as_string())
            print "邮件发送成功"
        except smtplib.SMTPException:
            print "Error: 无法发送邮件"
