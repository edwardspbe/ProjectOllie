from django.contrib.auth.models import User
from ProjectOllie.models import Profile
from django import forms

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)
        

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'cell_no', 'phone_no', 'bio', 'location', 'date')
        widgets = { 'bio':   forms.Textarea(attrs={'cols': 90, 'rows': 2}), 
                    'date':  forms.DateInput(attrs={'type': 'date'}),
        }


