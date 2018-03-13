from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from django.template.context_processors import csrf

def index(request):
    return render(request, 'ollie.html',)

