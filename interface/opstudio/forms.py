from django import forms
from django.forms import ModelForm

from .models import Digitiser
from .models import Language
from .models import Collection
from .models import Work
from .models import Text
from .models import Witness
from .models import WitnessIndex
from .models import WitnessPartition
from .models import WorkInCollection
from .models import Alignment
from .models import AlignmentType
from .models import AlignmentLog
from .models import Annotation
from .models import AnnotationContent
from .models import AnnotationLog
from .models import AnnotationType
from .models import AnnotationContentType
from .models import AnnotationCategory
from .models import AnnotationParent
from .models import Dictionary
from .models import DictionaryEntry

from .models import UserFile
from .models import UserSettings
from .models import UserTheme
from .models import UserRequest

from .models import CsvAlignment
from .models import CsvAlignmentList

#from .models import UserSettings
from .models import UserFile

class LoginForm(forms.Form):
    username = forms.CharField(label='username')
    password = forms.CharField(label='password')
    witness = forms.CharField(label='witness')
    #common = forms.CharField(label='username')
    #common2 = forms.CharField(label='username')
    #common3 = forms.CharField(label='username')


## new form for alignment 'optools' screen
class AlignmentForm(forms.Form):

    wit1content = forms.CharField(label='wit1content')
    wit2content = forms.CharField(label='wit2content')

    wit1start = forms.CharField(label='wit1start')
    wit1end = forms.CharField(label='wit1end')

    wit2start = forms.CharField(label='wit2start')
    wit2end = forms.CharField(label='wit2end')

    witness_src = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 1")
    witness_dst = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "Witness 2")

    subsegment = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "subsegment")

    otani = forms.ModelChoiceField(queryset=Witness.objects.all(), label = "otani")

    ngrams = forms.BooleanField(initial=False, required=False)
    dicts = forms.BooleanField(initial=True, required=False)
    alignments = forms.BooleanField(initial=False, required=False)


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

