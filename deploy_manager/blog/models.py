from __future__ import unicode_literals
from django.db import models

# Create your models here.

class Deploy_history(models.Model):
    staff_name = models.CharField(max_length=20)
    project_name = models.CharField(max_length=100)
    deploy_name = models.CharField(max_length=100)
    ip_name = models.CharField(max_length=1000)
    update_time = models.DateTimeField('update_time', auto_now_add=True)

    def __unicode__(self):
        return  self.staff_name

# Create your models here.

