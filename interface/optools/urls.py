from django.urls import path, re_path
from django.conf.urls import url
from django.contrib import admin

#from django.contrib.auth import views as auth_views

#from django.conf.urls.defaults import *

#from models import Note
from optools.models import Note

from . import views
notes = Note.objects.all()

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.create_alignment, name='create_alignment'),
    #path(r'^$', 'django.views.generic.list_detail.object_list', dict(queryset=notes)),
    #path('^$', views.note, name='note'),
    #path('<str:slug>/', views.create_note, name='create_note'),
    #path('<str:>/', views.sluggy, name='sluggy'),
    path('create/', views.create_alignment, name='create_alignment'),
    path('update/', views.update_alignment, name='update_alignment'),
    path('dictchk/', views.dict_chk, name='dict_chk'),
]

