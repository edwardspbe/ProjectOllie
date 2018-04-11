from django.contrib.auth.models import User
from ProjectOllie.models import Profile
from django import forms

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)
        fieldsets = (('',{ 'fields':('username',
                                    ('first_name','last_name'), 
                                      'email',)
                         } ))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'bio', 'location', 'date')
        fieldsets = (('',{ 'fields':(('location', 'date'), 
                                      'bio'), } ))
        widgets = {
                    'bio':    forms.Textarea(attrs={'cols': 70, 'rows': 5}),
        }


