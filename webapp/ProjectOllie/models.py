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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

PHONENO_CHOICES = (
    (0, 'alternate'),
    (1, 'primary'), 
)
class PhoneNo(models.Model):
    user = models.ForeignKey(User)
    number = models.CharField(max_length=15)
    state = models.SmallIntegerField('State', choices=PHONENO_CHOICES)


####################################################################################
#Ollie services
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
class OnCallDetails(models.Model):
    user = models.ForeignKey(User)
    phone_no = models.CharField(max_length=10)
    state = models.SmallIntegerField('State', choices=CALL_CHOICES)

####################################################################################
#Ollie monitors...
class Location(models.Model):
    name = models.CharField('Location', max_length=50)
    location = models.CharField('Details', max_length=200)
    coordinates = models.CharField('Coordinates', max_length=30)

class Camera(models.Model):
    name = models.CharField('Device Name', max_length=50)
    location = models.ForeignKey(Location)
    ipaddr = models.CharField('IP Addr', max_length=16)
    state = models.SmallIntegerField('State', choices=STATE_CHOICES)

LIGHT_STATE = (
    (0, 'off'), 
    (1, 'on'),
)
class Light(models.Model):
    location = models.ForeignKey(Location)
    state = models.SmallIntegerField('State', choices=LIGHT_STATE)

DOOR_STATE = (
    (0, 'closed'), 
    (1, 'open'),
)
class Door(models.Model):
    location = models.ForeignKey(Location)
    state = models.SmallIntegerField('State', choices=DOOR_STATE)


