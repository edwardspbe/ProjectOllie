"""ProjectOllie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from ProjectOllie import views
from django.contrib.auth import views as auth_views

admin.site.site_title = 'Sandy Beach at Otter Lake'
admin.site.site_header = 'Sandy Beach at Otter Lake Intranet'
admin.site.index_title = 'Sandy Beach at Otter Lake Intranet Administration'

handler400 = 'ProjectOllie.views.handler400'
handler403 = 'ProjectOllie.views.handler400'
handler404 = 'ProjectOllie.views.handler400'
handler500 = 'ProjectOllie.views.handler400'


urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'admin/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'profile/', views.profile),
    #url(r'profile/(?P<user>\w)', views.profile),
    url(r'get_light/', views.get_light),
    url(r'set_light/', views.set_light),
    url(r'get_door/', views.get_door),
    url(r'set_door/', views.set_door),
    url(r'get_location/', views.get_location),
    url(r'set_location/', views.set_location),
    url(r'^$', views.index, name='index'),
]
