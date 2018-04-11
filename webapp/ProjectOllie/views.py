from django.http import HttpResponse
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context, loader
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib import messages
from ProjectOllie.forms import UserForm, ProfileForm
from ProjectOllie.models import Profile

#@permission_required('ProjectOllie.Administrator', login_url='/')
def index(request):
    t = loader.get_template( 'index.html' )
    c = {'user': request.user, }
    c.update( csrf( request ) )
    return HttpResponse( t.render( c ) )

def handler400(request):
    response = render_to_response('400.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('/')
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
       


#    user = models.ForeignKey(User)
#    bio = models.TextField(max_length=500, blank=True)
#    location = models.CharField(max_length=30, blank=True)
#    address = models.CharField(max_length=30, blank=True)
#    date = models.DateField(null=True, blank=True)

def get_light(request, location):
    if request.method == 'GET':
        pass
    else :
        return 255

def set_light(request):
    if request.method == 'POST':
        pass
    else :
        return 255

def get_door(request, location):
    if request.method == 'GET':
        pass
    else :
        return 255

def set_door(request):
    if request.method == 'POST':
        pass
    else :
        return 255

def get_location(request, location):
    if request.method == 'GET':
        pass
    else :
        return 255

def set_location(request):
    if request.method == 'POST':
        pass
    else :
        return 255


