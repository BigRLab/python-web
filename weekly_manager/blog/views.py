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
from blog.models import Weekly_report
import time
import json
import re

def home(request):
    return render_to_response('login.html')

@login_required
def index(request):
    return render_to_response('weekly_report_details.html')

@login_required
def weekly_report_add(request):
    return render_to_response('weekly_report_add.html')

@login_required
def chpasswd(request):
    return render_to_response('chpasswd.html')

#######################
#周报代码
#######################

def weekly_db_write(table, staff_name, start_time, end_time, report_content):
    print  staff_name, start_time, end_time, report_content
    blog = table
    blog.staff_name = staff_name
    blog.start_time = start_time
    blog.end_time = end_time
    blog.report_content = report_content
    blog.save()
    return HttpResponse(json.dumps("ok"))

def weekly_db_update(staff_name, start_time, end_time, report_content):
    print  staff_name, start_time, end_time, report_content
    blog = Weekly_report.objects.get(staff_name=staff_name,start_time=start_time,end_time=end_time)
    blog.report_content = report_content
    blog.save()
    return HttpResponse(json.dumps("ok"))

@login_required
def report_add(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        start_time = request.POST.get('start_time','')
        end_time = request.POST.get('end_time','')
        report_content = request.POST.get('report_content','')
        print report_content
        print user_name,staff_name,start_time,end_time,report_content
        blog = Weekly_report.objects.filter(staff_name=staff_name,start_time=start_time,end_time=end_time)
        result_content = ""
        for i in blog:
            if i != "":
                result_content = i
        if result_content == "":
            db_result = weekly_db_write(Weekly_report(),staff_name=staff_name, start_time=start_time, end_time=end_time, report_content=report_content)
        else:
            db_result = weekly_db_update(staff_name=staff_name, start_time=start_time, end_time=end_time, report_content=report_content)
        return HttpResponse(json.dumps(0))
    else:
        return  render_to_response('weekly_report_add.html')

@login_required
def report_details(request):
    if request.method == "GET":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        limit = 10
        page = request.GET.get('page')
        if user_name == "admin":
            report_content = ""
            report_his = Weekly_report.objects.all().order_by("-update_time") 
        else:
            report_his = Weekly_report.objects.filter(staff_name=staff_name).order_by("-update_time")

        paginator = Paginator(report_his, limit)
        try:
            show_details = paginator.page(page)
        except  PageNotAnInteger:
            show_details = paginator.page(1)
        except EmptyPage:
            show_details = paginator.page(paginator.num_pages)
        t = loader.get_template("weekly_report_details.html")
        c = Context({'report_his': show_details,'staff_name': staff_name})
        return HttpResponse(t.render(c))

@login_required
def this_week_content(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        start_time = request.POST.get('start_time','')
        end_time = request.POST.get('end_time','')
        report_his = Weekly_report.objects.filter(staff_name=staff_name,start_time=start_time,end_time=end_time).values()

        print "====" * 50
        print report_his
        result_content = ""
        for i in report_his:
            result_content = i['report_content']
        #print type(result_content)
        #t = loader.get_template("weekly_report_add.html")
        #c = Context({'result_content':result_content})
        return HttpResponse(json.dumps(result_content))
       
        #return HttpResponse(t.render(c))
    else:
        return  render_to_response('weekly_report_add.html')

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
                response = HttpResponseRedirect('/index.html')
                #response = HttpResponseRedirect('/weekly_report_details.html')
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
