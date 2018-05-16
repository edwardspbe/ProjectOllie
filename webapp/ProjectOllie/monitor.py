from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from ProjectOllie.forms import UserForm, ProfileForm
from ProjectOllie.models import Profile, Location, Device
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


#handler for unknown devices...
def handle_device_does_not_exist():
    pass

#default (heartbeat) from monitored location to Ollie. Should report in based on configured
#period.  We will return configured tasks every time to facilitate quick changeovers
#for monitored devices.
@csrf_exempt
def checkin(request):
    location = request.META.get('REMOTE_ADDR')
    loc = ()
    try: 
        loc = Location.objects.get(location=location)
    except ObjectDoesNotExist: 
        #hmmm, unknown device is trying to communicate with us...  log their IP for now.
        print "Error: IP: %s tried to checkin with (hsot: %s, status: %s, location: %s, state: %s" \
              % (request.META.get('REMOTE_ADDR'),host,status, location, state)
        loc = Location.objects.create(name='', status=0, state=2, location=location) 
    #save so that our heartbeat timer is updated...
    loc.save()
    
    #return the devices this location is required to monitor
    devdetails = () 
    devices = Device.objects.filter(location=location)
    for dev in devices:
        devdetails.append(dev.name)
    return JsonResponse({'status': 'success', 'devices': devdetails})

#interface for reporting device state changes
@csrf_exempt
def dev_state(request):
    ip = request.META.get('REMOTE_ADDR')
    if request.method == "POST":
       name = request.POST.get("name", "")
       status = request.POST.get("status", "") 
       try: 
           location = Location.objects.get(ipaddr=ip)
           dev = Device.objects.get(location=location, name=name)
       except ObjectDoesNotExist:
           handle_device_does_not_exist()
           return JsonResponse({'status': 'error'})

       dev.status = status
       dev.save()
       return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})
    

