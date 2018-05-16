# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ProjectOllie.models import Location, Device, Profile, Alarm, Notifications, Function
from django.contrib import admin, messages
from django.http import HttpResponse,HttpResponseRedirect

# Register your models here.

class LocationAdmin( admin.ModelAdmin ):
    list_display = ( 'name', 'state', 'ipaddr', 'location', 'coordinates', 'time' )
    fields = [ 'name', ('state', 'time',), ('ipaddr', 'coordinates', 'location',), ] 
    actions = ['enablelocation']

    def enablelocation( self, request, queryset):
        updated = queryset.update( state=1)
        self.message_user( request, "%s locations enabled." % updated )
        return HttpResponseRedirect(request.get_full_path())
    enablelocation.short_description = "Enable selected locations"

class FunctionAdmin( admin.ModelAdmin ):
    list_display = ( 'type', 'handler' )
    fields = [ 'type', 'handler' ] 

class DeviceAdmin( admin.ModelAdmin ):
    list_display = ( 'name', 'location', 'state', 'function', 'status' )
    fields = [ 'name', 'location', 'state', 'function', 'status' ] 
    actions = [ 'enable_device' ]

    def enable_device(modeladmin, request, queryset):
        queryset.update(state=1)
    enable_device.short_description = "Enable selected devices"

class ProfileAdmin( admin.ModelAdmin ):
    list_display = ( 'user', 'bio', 'location', 'address', 'cell_no', 'phone_no', 'date')
    fields = ['user', 'bio', 'location', 'address', 'cell_no', 'phone_no', 'date' ]

class AlarmAdmin( admin.ModelAdmin ):
    list_display = ( 'device', 'time')
    fields = ['device', 'time']

class NotificationsAdmin( admin.ModelAdmin ):
    list_display = ( 'type', 'alarm', 'time')
    fields = ['type', 'alarm', 'time']
    
admin.site.register( Location, LocationAdmin )
admin.site.register( Function, FunctionAdmin )
admin.site.register( Device, DeviceAdmin )
admin.site.register( Profile, ProfileAdmin )
admin.site.register( Alarm, AlarmAdmin )
admin.site.register( Notifications, NotificationsAdmin )
