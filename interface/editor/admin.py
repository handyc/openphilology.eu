from django.contrib import admin

# Register your models here.

admin.site.site_header = "Open Philology";
admin.site.site_title = "Open Philology";

######################################################################

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
from .models import AnnotationLog
from .models import AnnotationType
from .models import AnnotationCategory
from .models import AnnotationParent
from .models import Dictionary
from .models import DictionaryEntry

######################################################################

@admin.register(Digitiser)
class DigitiserAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso', 'bcp47')
    list_filter = ('name', 'iso', 'bcp47')
    fields = ('name', 'iso', 'bcp47')

######################################################################

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('name','work','language',)
    list_filter = ('name','work','language',)
    fields = ('name','work','language',)

######################################################################

@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'digitiser')
    list_filter = ('name', 'text', 'digitiser')
    fields = ('name', 'text', 'digitiser')

######################################################################

@admin.register(WitnessIndex)
class WitnessIndexAdmin(admin.ModelAdmin):
    list_display = ('witness', 'filename', 'char_start', 'char_end', 'note',)
    list_filter = ('witness', 'filename', 'char_start', 'char_end', 'note',)
    fields = ('witness', 'filename', 'char_start', 'char_end', 'note')

######################################################################

@admin.register(WitnessPartition)
class WitnessPartitionAdmin(admin.ModelAdmin):
    list_display = ('witness', 'content', 'char_start', 'char_end',)
    list_filter = ('witness',)
    fields = ('witness', 'content', 'char_start', 'char_end',)

######################################################################

@admin.register(WorkInCollection)
class WorkInCollectionAdmin(admin.ModelAdmin):
    list_display = ('work', 'collection', 'number',)
    list_filter = ('work', 'collection', 'number',)
    fields = ('work', 'collection', 'number',)

######################################################################

@admin.register(Alignment)
class AlignmentAdmin(admin.ModelAdmin):
    list_display = ('witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type',)
    list_filter = ('witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type',)
    fields = ('witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type',)

######################################################################

@admin.register(AlignmentType)
class AlignmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(AlignmentLog)
class AlignmentLogAdmin(admin.ModelAdmin):
    list_display = ('alignment', 'witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type', 'user', 'date',)
    #list_filter = ('alignment', 'witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type', 'user', 'date',)
    list_filter = ('user', 'date',)
    fields = ('alignment', 'witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type',)

######################################################################

@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('witness', 'char_start', 'char_end', 'type', 'category', 'json_content',)
    #list_filter = ('witness', 'char_start', 'char_end', 'type', 'category', 'json_content',)
    list_filter = ('witness', 'type',)
    fields = ('witness', 'char_start', 'char_end', 'type', 'category', 'json_content',)

######################################################################

@admin.register(AnnotationLog)
class AnnotationLogAdmin(admin.ModelAdmin):
    list_display = ('annotation', 'witness', 'char_start', 'char_end', 'user', 'date',)
    #list_filter = ('annotation', 'witness', 'char_start', 'char_end', 'certainty', 'user', 'date',)
    list_filter = ('user', 'date',)
    fields = ('annotation', 'witness', 'char_start', 'char_end',)

######################################################################

@admin.register(AnnotationType)
class AnnotationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(AnnotationCategory)
class AnnotationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent',)
    list_filter = ('name', 'parent',)
    fields = ('name', 'parent',)

######################################################################

@admin.register(AnnotationParent)
class AnnotationParentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

######################################################################

@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    list_display = ('entry1', 'entry2', 'dictionary',)
    list_filter = ('dictionary',)
    fields = ('entry1', 'entry2', 'dictionary',)

######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################


