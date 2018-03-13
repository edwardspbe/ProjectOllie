from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from datetime import date


STATE_CHOICES = (
    (0, 'disabled'), 
    (1, 'enabled'),
)
CALL_CHOICES = (
    (0, 'disabled'), 
    (1, 'allmsgs'),
    (2, 'maintenance'),
    (3, 'service'),
)

class Camera(models.Model):
    name = models.CharField('Device Name', max_length=50)
    location = models.CharField('Device Location', max_length=200)
    ipaddr = models.CharField('IP Addr', max_length=16)
    state = models.SmallIntegerField('State', choices=STATE_CHOICES)

class ContactDetails(models.Model):
    name = models.ForeignKey(User)
    phone_no = models.CharField(max_length=10)
    state = models.SmallIntegerField('State', choices=CALL_CHOICES)


    
