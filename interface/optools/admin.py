from django.contrib import admin

# Register your models here.

admin.site.site_header = "Open Philology";
admin.site.site_title = "Open Philology";

from .models import UserFile
from .models import UserSettings
from .models import UserTheme
from .models import UserRequest

#from editor.models import Witness

###

@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('csvfile','witness_src','witness_dst',)
    list_filter = ('csvfile','witness_src','witness_dst',)
    fields = ('csvfile','witness_src','witness_dst',)

    def __str__(csvfile):
        return self.csvfile

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('username','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily',)
    list_filter = ('username',)
    fields = ('username','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily',)

    def __str__(self):
        return self.username

@admin.register(UserTheme)
class UserThemeAdmin(admin.ModelAdmin):
    list_display = ('name','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily',)
    list_filter = ('name',)
    fields = ('name','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily',)

    def __str__(self):
        return self.name

@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    list_display = ('request', 'status',)
    list_filter = ('request', 'status',)
    fields = ('request', 'status',)

    def __str__(self):
        return self.request

