from __future__ import unicode_literals
from django.db import models

# Create your models here.

class Property_operation_history(models.Model):
    staff_name = models.CharField(max_length=1000)
    ip_name = models.CharField(max_length=100000)
    operation_name = models.CharField(max_length=100000, blank=True, null=True)
    update_time = models.DateTimeField('update_time', auto_now_add=True)

class Property_content(models.Model):
    team_name = models.CharField(max_length=100, blank=True, null=True)
    domain_name = models.CharField(max_length=1000, blank=True, null=True)
    ip_name = models.CharField(max_length=100)
    ip_remark = models.CharField(max_length=100, blank=True, null=True)
    app_name = models.CharField(max_length=100, blank=True, null=True)
    system_name = models.CharField(max_length=100, blank=True, null=True)
    principal_name = models.CharField(max_length=100, blank=True, null=True)
    xen_name = models.CharField(max_length=100, blank=True, null=True)
    room_name = models.CharField(max_length=100, blank=True, null=True)
    xen_ip = models.CharField(max_length=100, blank=True, null=True)
    host_cpu = models.CharField(max_length=100, blank=True, null=True)
    host_memory = models.CharField(max_length=100, blank=True, null=True)
    host_disk = models.CharField(max_length=100, blank=True, null=True)
    server_model = models.CharField(max_length=100, blank=True, null=True)
    update_time = models.DateTimeField('update_time', auto_now_add=True)
    class Meta:
        unique_together = ("team_name", "ip_name")

