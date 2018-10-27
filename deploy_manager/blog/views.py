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
from blog.models import Deploy_history
import blog.ansible_deploy
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

#######################
#软件部署代码
#######################

def deploy_db_write(table, staff_name, project_name, deploy_name, ip_name):
    print  staff_name, project_name, deploy_name, ip_name
    blog = table
    blog.staff_name = staff_name
    blog.project_name = project_name
    blog.deploy_name = deploy_name
    blog.ip_name = ip_name
    blog.save()
    return HttpResponse(json.dumps("ok"))

@login_required
def project_deploy_install(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        project_name = request.POST.get('project_name','')
        deploy_name = request.POST.get('deploy_name','')
        ip_name = request.POST.get('ip_name','')
        logpath_name = request.POST.get('logpath_name','')
        logpath_topic = request.POST.get('logpath_topic','')
        process_name = request.POST.get('process_name','')
        app_zabbix = request.POST.get('app_zabbix','')
        file_dir="./roles"
        temp_dir = tempfile.mkdtemp(suffix=project_name, prefix=deploy_name, dir=file_dir)
        temp_dir_name = temp_dir.split('/')[-1]
        project_hosts_list=tempfile.NamedTemporaryFile(prefix=deploy_name, suffix="hosts",dir=file_dir)
        project_plybook_file=tempfile.NamedTemporaryFile(prefix=deploy_name, suffix=".yml",dir=file_dir)
        project_hosts_list.writelines(['[%s]\n' % deploy_name, '%s\n' % ip_name])
        project_hosts_list.seek(0)
        project_plybook_file.writelines(['- hosts: %s\n' % deploy_name, '  roles:\n', '     - { role: %s }\n' % temp_dir_name])
        project_plybook_file.seek(0)
        if project_name == "tomcat-7":
            shutil.copytree('./roles/tomcat-7/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
        elif project_name == "tomcat-8":
            shutil.copytree('./roles/tomcat-8/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
        elif project_name == "redis":
            shutil.copytree('./roles/redis/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
        elif project_name == "rabbitmq":
            shutil.copytree('./roles/rabbitmq/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
        elif project_name == "logstash":
            shutil.copytree('./roles/logstash/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
            logstash_defaults_file=tempfile.NamedTemporaryFile(prefix=deploy_name, suffix=".yml", dir="./roles/%s/defaults" % temp_dir_name)
            logstash_defaults_file.writelines(['logstash_apps:\n', '   - app_name: logstash\n', '     app_log:  %s\n' % logpath_name, '     app_type: %s-%s\n' % (logpath_topic, deploy_name), '     app_tags: %s\n' % deploy_name,'     app_topic: %s\n' % logpath_topic,'     app_project: %s' % deploy_name])
            logstash_defaults_file.seek(0)
            os.rename(logstash_defaults_file.name, './roles/%s/defaults/main.yml' % temp_dir_name)
        elif project_name == "zabbix":
            shutil.copytree('./roles/zabbix/', './roles/%s' % deploy_name)
            os.rename('./roles/%s' % deploy_name, temp_dir) 
            project_defaults_file=tempfile.NamedTemporaryFile(prefix=deploy_name, suffix=".yml", dir="./roles/%s/defaults" % temp_dir_name)
            project_defaults_file.writelines(['zabbix_apps:\n', '   - app_service:  %s\n' %deploy_name  , '     process_name: %s\n' % process_name, '     app_zabbix:  %s\n' % app_zabbix])
            project_defaults_file.seek(0)
            os.rename(project_defaults_file.name, './roles/%s/defaults/main.yml' % temp_dir_name)
        print project_hosts_list.name
        print project_plybook_file.name
        project_install=blog.ansible_deploy.run_playbook(project_hosts_list.name,project_plybook_file.name)
        project_hosts_list.close()
        project_plybook_file.close()
        shutil.rmtree(temp_dir)
        print "=" * 20
        print staff_name, project_name, deploy_name, ip_name
        db_result = deploy_db_write(Deploy_history(),staff_name=staff_name, project_name=project_name, deploy_name=deploy_name, ip_name=ip_name)
        if project_install == 0:
             return HttpResponse(json.dumps(project_install))
        else:
             return HttpResponse(json.dumps(project_install))
    else:
        return  render_to_response('deploy.html')

@login_required
def deploy_history_details(request):
    if request.method == "GET":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        limit = 10
        page = request.GET.get('page')
        deploy_his = Deploy_history.objects.all().order_by("-update_time") 

        paginator = Paginator(deploy_his, limit)
        try:
            show_details = paginator.page(page)
        except  PageNotAnInteger:
            show_details = paginator.page(1)
        except EmptyPage:
            show_details = paginator.page(paginator.num_pages)
        t = loader.get_template("deploy_details.html")
        c = Context({'deploy_his': show_details})
        return HttpResponse(t.render(c))

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
