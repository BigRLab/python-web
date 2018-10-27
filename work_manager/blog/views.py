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
from blog.models import Work_time
import time
import json
import re

def home(request):
    return render_to_response('login.html')

@login_required
def work_add(request):
    return render_to_response('work_add.html')

@login_required
def index(request):
    return render_to_response('work_details.html')

@login_required
def chpasswd(request):
    return render_to_response('chpasswd.html')

#######################
#加班制度代码
#######################


def work_db_write(table, staff_name, start_time, end_time, duration_number, type_name, development_name, reason_explain):
    print  staff_name, start_time, end_time, type_name, development_name, reason_explain
    blog = table
    blog.staff_name = staff_name
    blog.start_time = start_time
    blog.end_time = end_time
    blog.duration_number = duration_number
    blog.type_name = type_name
    blog.development_name = development_name
    blog.reason_explain = reason_explain
    blog.save()
    return HttpResponse(json.dumps("ok"))

@login_required
def work_record_delete(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = request.POST.get('staff_name','').replace('\t','').replace('\n','').replace(' ','')
        start_time = request.POST.get('start_time','').replace('\t','').replace('\n','')[-40:-24]
        end_time = request.POST.get('end_time','').replace('\t','').replace('\n','')[-40:-24]
        print staff_name,start_time,end_time
        db_delete = Work_time.objects.filter(staff_name=staff_name,start_time=start_time,end_time=end_time).delete()
        return HttpResponse(json.dumps(0))
    else:
        return  render_to_response('work_admin_details.html')

@login_required
def work_record_write(request):
    if request.method == "POST":
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        start_time = request.POST.get('start_time','')
        end_time = request.POST.get('end_time','')
        Type_name = request.POST.get('type_name','')
        development_name = request.POST.get('development_name','')
        reason_explain = request.POST.get('reason_explain','')
        if Type_name == "resttime":
            type_name = "调休"
        else:
            type_name = "加班"
        time_number=time_calculate(start_time=start_time, end_time=end_time, Type_name=Type_name)
        if Type_name == "resttime":
            duration_number = -time_number
        else:
            duration_number = time_number
        db_result = work_db_write(Work_time(),staff_name=staff_name, start_time=start_time, end_time=end_time, duration_number=duration_number, type_name=type_name, development_name=development_name, reason_explain=reason_explain)
        return HttpResponse(json.dumps(0))
    else:
        return  render_to_response('work_add.html')

@login_required
def work_admin_record_details(request):
    if request.method == "GET":
        user_name = request.COOKIES.get('username','')
        staff_name = request.GET.get('search','')
        search_name = staff_name
        start_time = request.GET.get('start_time','')
        end_time = request.GET.get('end_time','')
        work_condition = {}
        if staff_name != "":
            work_condition["staff_name__contains"] = staff_name
        if start_time != "":
            if end_time != "":
                work_condition["start_time__range"] = (start_time, end_time)
        if not work_condition :
            work_his = Work_time.objects.all().order_by("-update_time")
        else:
            work_his = Work_time.objects.filter(**work_condition).order_by("-update_time")
        page = request.GET.get('page')
        if page == "all":
            work_time = Work_time.objects.filter(staff_name=staff_name).aggregate(Sum('duration_number'))
            staff_name = staff_name.encode('utf-8')
            work_content = "%s ：还剩下 %s 小时的加班时长！！！" % (staff_name, work_time['duration_number__sum'])
            t = loader.get_template("work_admin_details.html")
            c = Context({'work_his': work_his,'staff_name': staff_name, 'work_time': work_content, 'user_name': user_name, 'search_name': search_name, 'start_time': start_time, 'end_time': end_time})
            return HttpResponse(t.render(c))
        else:
            limit = 10
            work_time = Work_time.objects.filter(staff_name=staff_name).aggregate(Sum('duration_number'))
            staff_name = staff_name.encode('utf-8')
            work_content = "%s ：还剩下 %s 小时的加班时长！！！" % (staff_name, work_time['duration_number__sum'])
            print staff_name
            print work_content
            paginator = Paginator(work_his, limit)
            try:
                show_details = paginator.page(page)
            except  PageNotAnInteger:
                show_details = paginator.page(1)
            except EmptyPage:
                show_details = paginator.page(paginator.num_pages)
            t = loader.get_template("work_admin_details.html")
            c = Context({'work_his': show_details,'staff_name': staff_name, 'work_time': work_content, 'user_name': user_name, 'search_name': search_name, 'start_time': start_time, 'end_time': end_time})
            return HttpResponse(t.render(c))

@login_required
def work_record_details(request):
    if request.method == "GET":
        #staff_name = request.COOKIES.get('username','')
        user_name = request.COOKIES.get('username','')
        staff_name = user_info(user_name)
        limit = 10
        page = request.GET.get('page')
        if user_name == "admin":
            work_content = ""
            work_his = Work_time.objects.all().order_by("-update_time")
            print staff_name
            for all_staff in staff_name:
                work_time = Work_time.objects.filter(staff_name=all_staff).aggregate(Sum('duration_number'))
                all_staff = all_staff.encode('utf-8')
                if work_time['duration_number__sum'] == None:
                    continue
                #staff_content = ("%s ：你还有 %s 小时，时间所剩不多啦." % (all_staff, work_time['duration_number__sum'])).encode('utf-8')
                #work_content[all_staff] = work_time['duration_number__sum']
                work_content = work_content + "%s: %s 小时   .|.   " % (all_staff, work_time['duration_number__sum']) + "\n" 
                #staff_content = " ：你还有 %d 小时，时间所剩不多啦！！！" %  work_time['duration_number__sum']
                #work_content.append(staff_content.decode('utf-8'))
                print work_content
                
        else:
            work_his = Work_time.objects.filter(staff_name=staff_name).order_by("-update_time")
            work_time = Work_time.objects.filter(staff_name=staff_name).aggregate(Sum('duration_number'))
            staff_name = staff_name.encode('utf-8')
            work_content = "%s ：你还有 %s 小时，时间所剩不多啦！！！" % (staff_name, work_time['duration_number__sum'])
            #work_content = " ：你还有 %d 小时，时间所剩不多啦！！！" % work_time['duration_number__sum']

        paginator = Paginator(work_his, limit)
        try:
            show_details = paginator.page(page)
        except  PageNotAnInteger:
            show_details = paginator.page(1)
        except EmptyPage:
            show_details = paginator.page(paginator.num_pages)
        if user_name == "admin":
            t = loader.get_template("work_admin_details.html")
        else:
            t = loader.get_template("work_details.html")
        c = Context({'work_his': show_details,'staff_name': staff_name, 'work_time': work_content, 'user_name':user_name})
        return HttpResponse(t.render(c))

def time_calculate(start_time, end_time, Type_name):
    start_format=time.strptime(start_time, "%Y-%m-%d %H:%M")
    end_format=time.strptime(end_time,"%Y-%m-%d %H:%M")
    start_second=time.mktime(start_format)
    end_second=time.mktime(end_format)
    time_result=round(float(end_second - start_second)/3600,1)
    if int(str(time_result)[-1]) >= 5:
        time_result=float(str(time_result)[:-2]) + float(0.5)
    else:
        time_result=float(str(time_result)[:-2])
    if int(start_time[-5:-3]) < 12:
        if int(end_time[-5:-3]) > 12:
            time_result = time_result - float(1)
    return time_result

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
                response = HttpResponseRedirect('/work_details.html')
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
