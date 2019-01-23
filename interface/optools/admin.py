from django.contrib import admin

# Register your models here.

admin.site.site_header = "Open Philology";
admin.site.site_title = "Open Philology";

###

#from .models import Witness

#from .models import Section
#from .models import SectionAlignment

###

#@admin.register(Section)
#class Section(admin.ModelAdmin):
#    list_display = ('witness', 'number', 'content', 'notes',)
#    list_filter = ('witness', 'number',)
#    fields = ('witness', 'number', 'content', 'notes',)

###

#@admin.register(SectionAlignment)
#class SectionAlignment(admin.ModelAdmin):
#    list_display = ('witness1', 'section1', 'witness2', 'section2', 'bleuvalue',)
#    #list_filter = ('witness1', 'section1',)
#    #list_filter = ('number',)
#    fields = ('section1', 'section2', 'bleuvalue')

###
