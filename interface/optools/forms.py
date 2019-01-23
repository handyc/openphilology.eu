from django import forms
from django.forms import ModelForm

from .models import SectionAlignment

class LoginForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password')
    witness = forms.CharField(label='witness')
    #common = forms.CharField(label='username')
    #common2 = forms.CharField(label='username')
    #common3 = forms.CharField(label='username')

