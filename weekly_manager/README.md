## 介绍
周报管理，记录周报信息，领导可查

### 环境准备
- running inside Linux
- python ( >= 2.7 )
- pip install Django==1.10.1
- pip install django-extensions 2.1.3
- pip install psycopg2 2.7.6.1
- yum install -y ansible 2.7.1
- pip install ansible==2.3.1
- yum install gcc
- yum install python-devel
- pip install pymssql-2.1.4

### 启动方法
>\# python manage.py createsuperuser
>\# python manage.py runserver 0.0.0.0:8000
>\# python manage.py migrate

#### 界面预览
1. 浏览器打开http://IP:8000
2. 输入刚才创建的账号密码

