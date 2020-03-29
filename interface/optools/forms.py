from django import forms
from django.forms import ModelForm

from editor.models import Witness
#from editor.models import Alignment

#from .models import UserSettings
from .models import UserFile

class LoginForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password')
    witness = forms.CharField(label='witness')
    #common = forms.CharField(label='username')
    #common2 = forms.CharField(label='username')
    #common3 = forms.CharField(label='username')

from django import forms

class UploadForm(forms.Form):
    csvfile = forms.FileField(
        label='Select a file',
        help_text='max. 10 megabytes'
    )

    witness_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 1")
    witness_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")

class AddAlignmentForm(forms.Form):
    witness_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 1")
    witness_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #char_start_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #char_end_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #char_start_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #char_end_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #score = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #type_id = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #witness_dst_id = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")
    #witness_src_id = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")

class NavigationForm(forms.Form):
    #left button 1
    #right button 1
    #partition select 1

    #left button 2
    #right button 2
    #partition select 2

    csvfile = forms.FileField(
        label='Select a file',
        help_text='max. 10 megabytes'
    )

    witness_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 1")
    witness_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")

class AlignmentForm(forms.Form):
    csvfile = forms.FileField(
        label='Select a file',
        help_text='max. 10 megabytes'
    )

    witness_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 1")
    witness_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")


