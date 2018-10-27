from __future__ import unicode_literals
from django.db import models

# Create your models here.

class Weekly_report(models.Model):
    staff_name = models.CharField(max_length=20)
    start_time = models.DateField()
    #start_time = models.DateTimeField(blank=True, null=True)
    #end_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateField()
    report_content = models.CharField(max_length=1000)
    update_time = models.DateTimeField('update_time', auto_now_add=True)

    def __unicode__(self):
        return  self.staff_name

# Create your models here.
