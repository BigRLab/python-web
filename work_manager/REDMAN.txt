pip install Django==1.10.1
pip install django-extensions 2.1.3
pip install psycopg2 2.7.6.1
yum install -y ansible 2.7.1
pip install ansible==2.3.1
yum install gcc
yum install python-devel
pip install pymssql-2.1.4
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
python manage.py migrate
