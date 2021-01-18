from django.contrib import admin

# Register your models here.

admin.site.site_header = "Open Philology Web Studio";
admin.site.site_title = "Open Philology Web Studio";

######################################################################

from .models import Digitiser
from .models import Language
from .models import Collection
from .models import Work
from .models import Text
from .models import Witness
from .models import WitnessIndex
from .models import WitnessPartition
from .models import WitnessAlignment
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
from .models import Ngram
from .models import NgramInWitness
from .models import Dictionary
from .models import DictionaryEntry
from .models import DictionaryLine

######################################################################

from .models import UserFile
from .models import UserSettings
from .models import UserTheme
from .models import UserRequest

from .models import CsvAlignment
from .models import CsvAlignmentList

######################################################################

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
    list_display = ('name', 'work', 'translation_of', 'language',)
    list_filter = ('name', 'work', 'language',)
    fields = ('name', 'work', 'translation_of', 'language',)

######################################################################

@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortname', 'text', 'digitiser')
    list_filter = ('name', 'shortname', 'text', 'digitiser')
    fields = ('name', 'shortname', 'text', 'digitiser')

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
######################################################################

@admin.register(WitnessAlignment)
class WitnessAlignmentAdmin(admin.ModelAdmin):
    list_display = ('witness1', 'witness2',)
    list_filter = ('witness1', 'witness2',)
    fields = ('witness1', 'witness2',)

######################################################################

@admin.register(WorkInCollection)
class WorkInCollectionAdmin(admin.ModelAdmin):
    list_display = ('work', 'collection', 'number',)
    list_filter = ('collection', 'work',)
    fields = ('work', 'number', 'collection',)

######################################################################

@admin.register(Alignment)
class AlignmentAdmin(admin.ModelAdmin):
    list_display = ('tentative_name','witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type','owner')
    list_filter = ('witness_src','owner')
    fields = ('tentative_name','witness_src', 'witness_dst', 'char_start_src', 'char_end_src', 'char_start_dst', 'char_end_dst', 'score', 'type','owner')

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
    list_display = ('witness', 'coordinate_on', 'annotation_content', 'char_start', 'char_end', 'type', 'category', 'json_content',)
    #list_filter = ('witness', 'char_start', 'char_end', 'type', 'category', 'json_content',)
    list_filter = ('witness', 'type',)
    fields = ('witness', 'coordinate_on', 'annotation_content', 'char_start', 'char_end', 'type', 'category', 'json_content',)

######################################################################

@admin.register(AnnotationContent)
class AnnotationContentAdmin(admin.ModelAdmin):
    list_display = ('type', 'content', 'language',)
    list_filter = ('content',)
    fields = ('type', 'content', 'language',)

######################################################################

@admin.register(AnnotationLog)
class AnnotationLogAdmin(admin.ModelAdmin):
    list_display = ('annotation', 'witness', 'char_start', 'char_end', 'user', 'date',)
    list_filter = ('user', 'date',)
    fields = ('annotation', 'witness', 'char_start', 'char_end',)

######################################################################

@admin.register(AnnotationType)
class AnnotationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

######################################################################

@admin.register(AnnotationContentType)
class AnnotationContentTypeAdmin(admin.ModelAdmin):
    list_display = ('description',)
    list_filter = ('description',)
    fields = ('description',)

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

@admin.register(Ngram)
class NgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

@admin.register(NgramInWitness)
class NgramInWitnessAdmin(admin.ModelAdmin):
    list_display = ('ngram','nsize', 'witness','frequency', 'weight',)
    list_filter = ('witness',)
    fields = ('ngram','nsize','witness','frequency','weight',)

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

@admin.register(DictionaryLine)
class DictionaryLineAdmin(admin.ModelAdmin):
    list_display = ('line', 'dictionary',)
    list_filter = ('dictionary',)
    fields = ('line', 'dictionary',)

######################################################################

######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################




#####

@admin.register(CsvAlignment)
class CsvAlignmentAdmin(admin.ModelAdmin):
    list_display = ('csvlist', 'w1match', 'w1matchlength', 'w1matchtarget', 'w1matchfound', 'w2match', 'w2matchlength', 'w2matchtarget', 'w2matchfound','score',)
    list_filter = ('csvlist','w1match', 'w1matchlength', 'w1matchtarget', 'w1matchfound', 'w2match', 'w2matchlength', 'w2matchtarget', 'w2matchfound','score',)
    fields = ('csvlist','w1match', 'w1matchlength', 'w1matchtarget', 'w1matchfound', 'w2match', 'w2matchlength', 'w2matchtarget', 'w2matchfound','score',)

    def __str__(csvlist):
        return self.csvlist

@admin.register(CsvAlignmentList)
class CsvAlignmentListAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    fields = ('name',)

    def __str__(name):
        return self.name

@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ('csvfile','witness_src','witness_dst',)
    list_filter = ('csvfile','witness_src','witness_dst',)
    fields = ('csvfile','witness_src','witness_dst',)

    def __str__(csvfile):
        return self.csvfile

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('username','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily','nsize1', 'nsize2',)
    list_filter = ('username',)
    fields = ('username','text1fg','text1bg','text2fg','text2bg','text3fg','text3bg','text4fg','text4bg','mainfg','mainbg','alignmentslistfg','alignmentslistbg','alignmentsfg','alignmentsbg','other1fg','other1bg','other2fg','other2bg','fontfamily','nsize1', 'nsize2',)

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

