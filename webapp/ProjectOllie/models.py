from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from datetime import date


####################################################################################
#Website functions and user properties
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField("Information", max_length=500, blank=True)
    location = models.CharField("Location", max_length=30, blank=True)
    address = models.CharField("Address", max_length=30, blank=True)
    date = models.DateField("Date Joined", null=True, blank=True)
    cell_no = models.CharField("Mobile No.", max_length=10, default="mobile")
    phone_no = models.CharField("Home No.", max_length=10, null=True, blank=True)

#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()


####################################################################################
#Ollie services
STATE_CHOICES = (
    (0, 'disabled'), 
    (1, 'enabled'),
    (2, 'unregistered'),
)
STATUS_CHOICES = (
    (0, 'off'), 
    (1, 'on'),
    (2, 'closed'), 
    (3, 'open'),
    (4, 'monitoring'),
    (5, 'waiting'),
)
CALL_CHOICES = (
    (0, 'disabled'), 
    (1, 'allmsgs'),
    (2, 'maintenance'),
    (3, 'service'),
)
class OnCallUser(models.Model):
    user = models.ForeignKey(User)
    state = models.SmallIntegerField('State', choices=CALL_CHOICES)

####################################################################################
#Ollie monitors...
#Monitoring locations
class Location(models.Model):
    name = models.CharField('Location', max_length=50)
    ipaddr = models.CharField('IP Addr', max_length=16, default=1)
    location = models.CharField('Details', max_length=200)
    coordinates = models.CharField('Coordinates', max_length=30)
    state = models.SmallIntegerField('State', choices=STATE_CHOICES, default=0)
    time = models.DateTimeField('Time', auto_now=True)

    def __str__(self):
        return self.name

#Monitoring function
class Function(models.Model):
    FUNCTION_CHOICES = (
        (0, 'light'), 
        (1, 'door'),
        (2, 'camera'),
        (3, 'button'),
        (4, 'wind'),
        (5, 'humidity'),
        (6, 'temperature'),
        (7, 'water'),
    )
    type = models.SmallIntegerField('Type', choices=FUNCTION_CHOICES)
    handler = models.TextField('Function Handler', null=True, blank=True)

    def __str__(self):
        return self.get_type_display()

    def handler_verbose(self):
        return dict(Function.FUNCTION_CHOICES)[self.flavor]

#Devices to be monitored
class Device(models.Model):
    name = models.CharField('Monitored Device', max_length=50)
    location = models.ForeignKey(Location, default=1)
    function = models.ForeignKey(Function, default=1)
    state = models.SmallIntegerField('State', choices=STATE_CHOICES)
    status = models.SmallIntegerField('Status', choices=STATUS_CHOICES, default=0)
    time = models.DateTimeField('Time', auto_now=True)

    def state_verbose(self):
        return dict(STATE_CHOICES)[self.flavor]

#Alarms raised on Lights, Doors and Video
class Alarm(models.Model):
    device = models.ForeignKey(Device, default=1)
    time = models.DateTimeField('Time', auto_now_add=True)

#Notifications result from critical alarms being raised.
class Notifications(models.Model):
    NOTE_CHOICES = (
        (0, 'email'), 
        (1, 'sms'),
    )
    type = models.SmallIntegerField('Type', choices=NOTE_CHOICES)
    alarm = models.ForeignKey(Alarm, default=1)
    time = models.DateTimeField('Time', auto_now_add=True)



