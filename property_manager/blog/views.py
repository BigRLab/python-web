# Create your views here.
# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response,loader,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext,Context
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from blog.models import Property_operation_history
from blog.models import Property_content
import blog.ansible_property as ansible_property
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import time
import tempfile
import json
import os
import sys
import shutil
import re

def home(request):
    return render_to_response('login.html')

@login_required
def index(request):
    return render_to_response('index.html')

@login_required
def chpasswd(request):
    return render_to_response('chpasswd.html')

@login_required
def property_add(request):
    return render_to_response('property_add.html')

#######################
#资产代码
#######################

@login_required
def property_write(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        ip_name = request.POST.get('ip_name','')
        all_name = request.POST.get('all_name','')
        project_name = request.POST.get('project_name','')
        team_name_html = request.POST.get('team_name_html','')
        domain_name_html = request.POST.get('domain_name_html','')
        ip_remark_html = request.POST.get('ip_remark_html','')
        app_name_html = request.POST.get('app_name_html','')
        system_name_html = request.POST.get('system_name_html','')
        cpu_name_html = request.POST.get('cpu_name_html','')
        memory_name_html = request.POST.get('memory_name_html','')
        disk_name_html = request.POST.get('disk_name_html','')
        model_name_html = request.POST.get('model_name_html','')
        principal_name_html = request.POST.get('principal_name_html','')
        xen_name_html = request.POST.get('xen_name_html','')
        room_name_html = request.POST.get('room_name_html','')
        xen_ip_html = request.POST.get('xen_ip_html','')
        update_operation = request.POST.get('update_operation','')
        print "+++" * 200
        print project_name
        if update_operation == "update_operation":
            ip_name = ip_name.encode('utf-8')
            ip_name = ''.join(ip_name.split())
            ip_name = ''.join(ip_name.split("<nobr>"))
            ip_name = '\n'.join(ip_name.split("</nobr>"))
            print ip_name
        
        file_dir="./upload/property_tempfile"

        if project_name == "pool_all":
            operation_content = "添加池" 
            print operation_content
            for ip_name in ip_name.split("\n"):
                baseDir = os.path.dirname(os.path.abspath(__name__));
                hosts_filedir = os.path.join(baseDir,'upload', 'property_tempfile', time.strftime('%Y'), time.strftime('%m'), time.strftime('%d'));
                if not os.path.exists(hosts_filedir):
                    os.makedirs(hosts_filedir)
                property_hosts_list=tempfile.NamedTemporaryFile(prefix=ip_name, suffix="hosts",dir=file_dir)
                property_hosts_list.writelines(['[pool-ip]\n', '%s ansible_ssh_user=root ansible_ssh_pass=Zh@0P1n!123\n' % ip_name])
                property_hosts_list.seek(0)
                property_ip_file = ansible_property.run_adhoc(property_hosts_list.name, "script", "./blog/pool_info.sh")
                property_copy = ansible_property.run_adhoc(property_hosts_list.name, "synchronize", "mode=pull src=/tmp/%s dest=%s" % (ip_name, hosts_filedir))
                property_hosts_list.close()
                if property_copy == 0:
                    hosts_file_name = hosts_filedir+"/"+ip_name
                    property_info = property_write_db(hosts_file_name)
        elif project_name == "add_list":
            operation_content = "添加主机" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                print "==="
                print i
                print "==="
                if len(ip_exist) == 0:
                    property_info = property_db_write(Property_content(), team_name=team_name_html, domain_name=domain_name_html, ip_name=i, ip_remark=ip_remark_html, app_name=app_name_html, system_name=system_name_html, principal_name=principal_name_html, xen_name=xen_name_html, room_name=room_name_html, xen_ip=xen_ip_html, host_cpu=cpu_name_html, host_memory=memory_name_html, host_disk=disk_name_html, server_model=model_name_html)
        elif project_name == "room_list":
            operation_content = "更改机房位置" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.room_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "domain_list":
            operation_content = "更改域名" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.domain_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "principal_list":
            operation_content = "更改负责人" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.principal_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "app_list":
            operation_content = "更改应用" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.app_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "system_list":
            operation_content = "更改系统" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.system_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "team_list":
            operation_content = "更改团队" 
            print operation_content
            for i in ip_name.split("\n"):
                ip_exist = Property_content.objects.filter(ip_name=i)
                if len(ip_exist) != 0:
                    blog = Property_content.objects.get(ip_name=i)
                    blog.team_name=all_name
                    blog.save()
                    property_info = "0"
        elif project_name == "change_hosts":
            print "=======" * 20
            print ip_name,team_name_html,domain_name_html,ip_remark_html,app_name_html,system_name_html,principal_name_html,xen_name_html,room_name_html,xen_ip_html, cpu_name_html, memory_name_html, disk_name_html, model_name_html
            print "=======" * 20
            operation_content = "更改记录"
            print operation_content
            for i in ip_name.split("\n"):
                print "=======" * 20
                print i
                print "=======" * 20
                blog = Property_content.objects.get(ip_name=i)
                print "=======" * 20
                print blog
                print "=======" * 20
                blog.team_name=team_name_html
                blog.domain_name=domain_name_html
                blog.ip_remark=ip_remark_html
                blog.app_name=app_name_html
                blog.system_name=system_name_html
                blog.principal_name=principal_name_html
                blog.xen_name=xen_name_html
                blog.room_name=room_name_html
                blog.xen_ip=xen_ip_html
                blog.host_cpu=cpu_name_html
                blog.host_memory=memory_name_html
                blog.host_disk=disk_name_html
                blog.server_model=model_name_html
                blog.save()
                property_info = "0"
        else:
            return  render_to_response('property_add.html')

        print "===" * 100
        print property_info
        print "===" * 100
        if property_info == "0":
             result_operation="%s : %s" % (operation_content, str(all_name.encode('utf-8')))
             property_db_history(Property_operation_history(), staff_name, ip_name, operation_name=result_operation)
             return HttpResponse(json.dumps(property_info))
        else:
             return HttpResponse(json.dumps(property_info))
    else:
        return  render_to_response('property_add.html')

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
    return "0"

def property_send_mail(ip_name):
    property_send_info = "以下IP信息在xenserver中命名规范不符合标准，标准为：命名不能有空格，并且以ip开头加上-用处，如：(172.30.1.100-nginx)，赶紧去补，不然每天都发邮件，烦死你！！！\n\n"
    for i in ip_name:
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

    subject = '命名不规范IP'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message.as_string())
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

@login_required
def property_details(request):
    if request.method == "GET":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        search_team_name = request.GET.get('search_team','')
        search_domain_name = request.GET.get('search_domain','')
        search_ip_name = request.GET.get('search_ip','')
        search_remark_name = request.GET.get('search_remark','')
        search_app_name = request.GET.get('search_app','')
        search_system_name = request.GET.get('search_system','')
        search_xen_name = request.GET.get('search_xen_name','')
        search_xen_ip = request.GET.get('search_xen_ip','')
        rank_ip = request.GET.get('rank_ip')
        rank_domain = request.GET.get('rank_domain')
        rank_name = ""
        if rank_ip == "rank_ip":
            rank_name = "ip_name"
        elif rank_domain == "rank_domain":
            rank_name = "domain_name"
        property_condition = {}
        if search_team_name != "":
            property_condition["team_name__contains"] = search_team_name
        if search_domain_name != "":
            property_condition["domain_name__contains"] = search_domain_name
        if search_ip_name != "":
            property_condition["ip_name__contains"] = search_ip_name
        if search_remark_name != "":
            property_condition["ip_remark__contains"] = search_remark_name
        if search_app_name != "":
            property_condition["app_name__contains"] = search_app_name
        if search_system_name != "":
            property_condition["system_name__contains"] = search_system_name
        if search_xen_name != "":
            property_condition["xen_name__contains"] = search_xen_name
        if search_xen_ip != "":
            property_condition["xen_ip__contains"] = search_xen_ip
        if not property_condition :
            if rank_name != "":
                property_his = Property_content.objects.all().order_by(rank_name) 
            else:
                property_his = Property_content.objects.all().order_by("-update_time") 
        else:
            if rank_name != "":
                property_his = Property_content.objects.filter(**property_condition).order_by(rank_name)
            else:
                property_his = Property_content.objects.filter(**property_condition).order_by("-update_time")
        property_number=len(property_his)
        page = request.GET.get('page')
        if page == "all":
            t = loader.get_template("property_details.html")
            c = Context({'property_his': property_his, 'search_team_name': search_team_name, 'search_domain_name': search_domain_name, 'search_ip_name': search_ip_name, 'search_remark_name': search_remark_name, 'search_app_name': search_app_name, 'search_system_name': search_system_name, 'search_xen_name': search_xen_name, 'search_xen_ip': search_xen_ip, 'rank_ip': rank_ip, 'rank_domain': rank_domain})
            return HttpResponse(t.render(c))
        else:
            limit = 20
            paginator = Paginator(property_his, limit)
            try:
                show_details = paginator.page(page)
            except  PageNotAnInteger:
                show_details = paginator.page(1)
            except EmptyPage:
                show_details = paginator.page(paginator.num_pages)
            t = loader.get_template("property_details.html")
            c = Context({'property_his': show_details, 'search_team_name': search_team_name, 'search_domain_name': search_domain_name, 'search_ip_name': search_ip_name, 'search_remark_name': search_remark_name, 'search_app_name': search_app_name, 'search_system_name': search_system_name, 'search_xen_name': search_xen_name, 'search_xen_ip': search_xen_ip, 'rank_ip': rank_ip, 'rank_domain': rank_domain, 'property_number': property_number})
            return HttpResponse(t.render(c))

@login_required
def property_operation(request):
    if request.method == "GET":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        search_name = request.GET.get('search','')
        if search_name != "":
            property_his = Property_operation_history.objects.filter(ip_name__contains=search_name).order_by("-update_time") 
        else:
            property_his = Property_operation_history.objects.all().order_by("-update_time") 
        limit = 10
        page = request.GET.get('page')
        paginator = Paginator(property_his, limit)
        try:
            show_details = paginator.page(page)
        except  PageNotAnInteger:
            show_details = paginator.page(1)
        except EmptyPage:
            show_details = paginator.page(paginator.num_pages)
        t = loader.get_template("property_operation_history.html")
        c = Context({'property_his': show_details, 'search_ip_name': search_name})
        return HttpResponse(t.render(c))

@login_required
def property_record_delete(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        operation_content = "删除数据"
        ip_address = request.POST.get('ip_name','').replace('\t','').replace('\n','').replace(' ','')
        print "delete property !!!%s!!!" % ip_address
        property_db_history(Property_operation_history(), staff_name, ip_address, operation_name=operation_content)
        db_delete = Property_content.objects.filter(ip_name=ip_address).delete()
        #result_operation="%s : %s" % (operation_content, str(all_name))
         
        if db_delete[0] == 0:
            return HttpResponse(json.dumps(1))
        else:
            return HttpResponse(json.dumps(0))
        
    else:
        return  render_to_response('property_details.html')

@login_required
def property_record_query(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        ip_address = request.POST.get('ip_name','').replace('\t','').replace('\n','').replace(' ','')
        print "query property !!!%s!!!" % ip_address
        db_query = Property_content.objects.filter(ip_name=ip_address).values()
        for i in db_query:
            db_dict = i
        if "update_time" in db_dict.keys():
            del db_dict["update_time"]
        print db_dict
        #t=template.Template('[%s, {{ team_name }}, {{ domain_name }}, {{ ip_remark }}, {{ app_name }}, {{ system_name }}, {{ principal_name }}, {{ xen_name }}, {{ room_name }}, {{ xen_ip }}]' % ip_address)
        #c=Context(db_result)
        #print t.render(c)
        
        return HttpResponse(json.dumps(db_dict))

    else:
        return  render_to_response('property_details.html')

def property_db_history(table, staff_name=None, ip_name=None, operation_name=None):
    print "DB write history"
    print  staff_name, ip_name, operation_name
    blog = table
    blog.staff_name = staff_name
    blog.ip_name = ip_name
    blog.operation_name = operation_name
    blog.save()
    return HttpResponse(json.dumps("ok"))

def property_db_write(table, team_name=None, domain_name=None, ip_name=None, ip_remark=None, app_name=None, system_name=None, principal_name=None, xen_name=None, room_name=None, xen_ip=None, host_cpu=None, host_memory=None, host_disk=None, server_model=None):
    print "DB write"
    print  team_name, domain_name, ip_name, ip_remark, app_name, system_name, host_cpu, host_memory, host_disk, server_model, principal_name, xen_name, room_name, xen_ip
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
    #return HttpResponse(json.dumps("ok"))




def user_info(user_name):
    if user_name == "admin":
        Staff_info = User.objects.all()
        Staff_name = []
        for i in Staff_info:
            staff_info = User.objects.filter(username=str(i)).values()
            for staff_name in staff_info:
                Staff_name.append(staff_name['first_name'])
        return Staff_name
    else:
        staff_info = User.objects.filter(username=user_name).values()
        for staff_name in staff_info:
            return staff_name['first_name']

#######################
#######################
#登录代码
#######################

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                #response = HttpResponseRedirect('/index.html')
                response = HttpResponseRedirect('/property_details.html')
                response.set_cookie('username',username,86400)
                return response
            else:
                return  HttpResponse('Please check the user and password, login again!')
        else:
            return  HttpResponse('With the registered password is not correct!')
    else:
        return render_to_response('login.html')

def logout_view(request):
    logout(request)
    return render_to_response('login.html')

#######################
#改密代码
#######################

@login_required
def changepwd(request):
    if request.method == 'POST':
        user_name = request.COOKIES.get('username','')
        pass_name = request.POST.get('pass_name','')
        print pass_name
        u = User.objects.get(username__exact=user_name)
        u.set_password(pass_name)
        u_passwd = u.save()
        if u_passwd == None:
             return HttpResponse(json.dumps(0))
        else:
             return HttpResponse(json.dumps(1))
    else:
        return  render_to_response('index.html')
# Create your views here.
