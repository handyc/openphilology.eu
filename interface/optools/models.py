# Create your models here.

from django.db import models
from django.forms import ModelForm

#from django.contrib.auth import get_user_model

#from op.apps.editor.models import Witness
#from editor.models import Witness

#from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    text = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return u"Note(%s,%s)" % (self.title, self.slug)

    def get_absolute_url(self):
        return u"/optools/%s/" % self.slug
