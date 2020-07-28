from django.urls import path, re_path
from django.conf.urls import url
from django.contrib import admin

#from django.contrib.auth import views as auth_views

#from django.conf.urls.defaults import *

#from optools.models import Note

from . import views
#notes = Note.objects.all()

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.create_alignment, name='create_alignment'),
    path('create/', views.create_alignment, name='create_alignment'),
    path('update/', views.update_alignment, name='update_alignment'),
    path('add/', views.add_alignment, name='add_alignment'),
    path('navalign/', views.navalign, name='navalign'),
    path('delete/', views.delete_alignment, name='delete_alignment'),
    path('importer/', views.importer, name='importer'),
    #path('importer2/', views.importer2, name='importer2'),
    path('reader/', views.reader, name='reader'),
    #path('alignments/', views.alignments, name='alignments'),
    path('annotations/', views.annotations, name='annotations'),
    path('dictionaries/', views.dictionaries, name='dictionaries'),
    path('ngrams/', views.ngrams, name='ngrams'),
    path('embeddings/', views.embeddings, name='embeddings'),
    path('sts/', views.sts, name='sts'),
    path('visualisations/', views.visualisations, name='visualisations'),
    path('terminal/', views.terminal, name='terminal'),
    path('settings/', views.settings, name='settings'),
]

