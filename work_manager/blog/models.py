from __future__ import unicode_literals
from django.db import models

class Work_time(models.Model):
    staff_name = models.CharField(max_length=20)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    #date_number = models.CharField(max_length=20)
    duration_number = models.FloatField(blank=True, null=True)
    type_name = models.CharField(max_length=100)
    development_name = models.CharField(max_length=20)
    reason_explain = models.CharField(max_length=1000)
    update_time = models.DateTimeField('update_time', auto_now_add=True)

    def __unicode__(self):
        return  self.staff_name

# Create your models here.
