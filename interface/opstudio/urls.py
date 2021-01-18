from django.urls import include, path, re_path
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('alignments/', views.alignments, name='alignments'),
    #path('old/', views.old, name='old'),
    path('add/', views.add_alignment, name='add_alignment'),
    path('delete/', views.delete_alignment, name='delete_alignment'),
    path('navalign/', views.navalign, name='navalign'),
    path('importer/', views.importer, name='importer'),
    path('search/', views.search, name='search'),
    path('ngrams/', views.ngrams, name='ngrams'),
    path('update/', views.update_alignment, name='update_alignment'),
    path('upload/', views.upload, name='upload'),
    path('settings/', views.settings, name='settings'),
    path('accounts/', include('django.contrib.auth.urls')),
]


