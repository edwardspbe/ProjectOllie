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
from django.utils import timezone

def handler400(request):
    response = render_to_response('400.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def index(request):
    t = loader.get_template( 'index.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

def cabins(request):
    t = loader.get_template( 'cottages.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

def trailers(request):
    t = loader.get_template( 'trailers.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

def services(request):
    t = loader.get_template( 'services.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return HttpResponseRedirect(request.get_full_path())
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        try:
            profile_form = ProfileForm(instance=request.user.profile)
        except ObjectDoesNotExist :
            profile = Profile.objects.get_or_create(user=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile.html', {
                           'user_form': user_form,      
                           'profile_form': profile_form })
       

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required('ProjectOllie.Administrator', login_url='/park_state')
def notifications(request) :
    t = loader.get_template( 'notifications.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required('ProjectOllie.Administrator', login_url='/park_state')
def support(request) :
    t = loader.get_template( 'support.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

@login_required
@user_passes_test(lambda u: u.is_staff)
@permission_required('ProjectOllie.Administrator', login_url='/park_state')
def park_state(request) :
    state_details = {}
    for location in Location.objects.exclude(state=0) :
        state_details[location.name] = {}
        for device in Device.objects.filter(location=location,) :
            state_details[location.name][device.name] = device.get_status_display()
    t = loader.get_template( 'park_status.html' )
    c = {'user': request.user,
         'site_details': state_details,
    }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

