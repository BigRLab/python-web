"""python_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from blog import views

urlpatterns = [
    #url(r'^test/',views.test,name='test'),
    url(r'^$', views.home),
    url(r'^admin', include(admin.site.urls)),
    url(r'^login', views.login_view),
    url(r'^logout', views.logout_view),
    url(r'^changepwd', views.changepwd),
    url(r'^chpasswd', views.chpasswd),

    url(r'^property_add', views.property_add),
    url(r'^property_details', views.property_details),
    url(r'^property_operation', views.property_operation),
    url(r'^property_write', views.property_write),
    url(r'^property_delete', views.property_record_delete),
    url(r'^property_query', views.property_record_query),

]

