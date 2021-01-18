from django.db import models
from django.contrib.auth import get_user_model

from django.forms import ModelForm

######################################################################

# Open Philology Database Models
# 2 November 2020

######################################################################

######################################################################

# 1 Digitiser
# 2 Language
# 3 Collection
# 4 Work
# 5 Text
# 6 Witness
# 7 WitnessIndex
# 8 WitnessPartition
# 9 WitnessAlignment
# 10 WorkInCollection
# 11 Alignment
# 12 AlignmentType
# 13 AlignmentLog
# 14 Annotation
# 15 AnnotationContent
# 16 AnnotationLog
# 17 AnnotationType
# 18 AnnotationContentType
# 19 AnnotationCategory
# 20 AnnotationParent

# 21 Ngram
# 22 NgramInWitness
# 23 WordInWitness

# Agent

# 24 Dictionary
# 25 DictionaryEntry
# 26 DictionaryLine

######################################################################

class Digitiser(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "001. Digitisers"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Language(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "002. Languages"

    name = models.CharField(max_length=200, default="")
    iso = models.CharField(max_length=200, default="")
    bcp47 = models.CharField(max_length=200, default="", blank=True, null=True)

    def __str__(self):
        return self.name

######################################################################

class Collection(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "003. Collections"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Work(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "004. Works"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Text(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "005. Texts"

    name = models.CharField(max_length=200, default="")
    work = models.ForeignKey('Work', on_delete=models.SET_NULL, null=True, blank=True)
    translation_of = models.ForeignKey('Text', on_delete=models.SET_NULL, null=True, blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

######################################################################

class Witness(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "006. Witnesses"

    name = models.CharField(max_length=200, default="")
    shortname = models.CharField(max_length=200, default="", blank=~True, null=True)
    text = models.ForeignKey('Text', on_delete=models.SET_NULL, blank=True, null=True)
    digitiser = models.ForeignKey('Digitiser', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

######################################################################

class WitnessIndex(models.Model):
    class Meta:
        ordering = ('witness',)
        verbose_name_plural = "006b. Witness Indexes"

    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    filename = models.CharField(max_length=500, default="")
    note = models.CharField(max_length=500, default="")
    char_start = models.IntegerField()
    char_end = models.IntegerField()

    def __str__(self):
        return str(self.witness)

######################################################################

class WitnessPartition(models.Model):
    class Meta:
        ordering = ('witness','char_start',)
        verbose_name_plural = "006c. Witness Partitions"

    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=5000, default="")
    char_start = models.IntegerField()
    char_end = models.IntegerField()

    def __str__(self):
        return str(self.witness)

######################################################################
######################################################################

class WitnessAlignment(models.Model):
    class Meta:
        ordering = ('witness1','witness2',)
        verbose_name_plural = "006d. Witness Alignments"

    witness1 = models.ForeignKey('Witness', related_name='witness1', on_delete=models.SET_NULL, null=True)
    witness2 = models.ForeignKey('Witness', related_name='witness2', on_delete=models.SET_NULL, null=True)
    #char_start = models.IntegerField()
    #char_end = models.IntegerField()

    def __str__(self):
        return str(self.witness1)

######################################################################

class WorkInCollection(models.Model):
    class Meta:
        ordering = ('number', 'collection', 'work',)
        verbose_name_plural = "004b. Works in Collections"

    work = models.ForeignKey('Work', on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey('Collection', on_delete=models.SET_NULL, null=True)
    number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.number) + str(self.work)

######################################################################

class Alignment(models.Model):
    class Meta:
        ordering = ('witness_src','char_start_src')
        verbose_name_plural = "007. Alignments"

    tentative_name = models.CharField(max_length=50, blank=True, null=True, default="")
    witness_src = models.ForeignKey('Witness', related_name='witness_src', on_delete=models.SET_NULL, null=True)
    witness_dst = models.ForeignKey('Witness', related_name='witness_dst', on_delete=models.SET_NULL, null=True)
    char_start_src = models.IntegerField(blank=True, null=True)
    char_end_src = models.IntegerField(blank=True, null=True)
    char_start_dst = models.IntegerField(blank=True, null=True)
    char_end_dst = models.IntegerField(blank=True, null=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    #owner = models.ForeignKey('Witness', related_name='witness_src', on_delete=models.SET_NULL, null=True)

    score = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey('AlignmentType', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.witness_src)

######################################################################

class AlignmentType(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "007b. Alignment Types"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class AlignmentLog(models.Model):
    class Meta:
        ordering = ('-date', 'witness_src',)
        verbose_name_plural = "007c. Alignment Log Entries"

    alignment = models.ForeignKey('Alignment', on_delete=models.SET_NULL, null=True)
    witness_src = models.ForeignKey('Witness', related_name='witness_src_log', on_delete=models.SET_NULL, null=True)
    witness_dst = models.ForeignKey('Witness', related_name='witness_dst_log', on_delete=models.SET_NULL, null=True)
    char_start_src = models.IntegerField(blank=True, null=True)
    char_end_src = models.IntegerField(blank=True, null=True)
    char_start_dst = models.IntegerField(blank=True, null=True)
    char_end_dst = models.IntegerField(blank=True, null=True)
    score = models.IntegerField()
    type = models.ForeignKey('AlignmentType', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    #user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.score)

######################################################################

class Annotation(models.Model):
    class Meta:
        ordering = ('witness', 'char_start',)
        verbose_name_plural = "008. Annotations"

    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    coordinate_on = models.ForeignKey('Annotation', on_delete=models.SET_NULL, null=True)
    annotation_content = models.ForeignKey('AnnotationContent', on_delete=models.SET_NULL, null=True)
    char_start = models.IntegerField()
    char_end = models.IntegerField()
    type = models.ForeignKey('AnnotationType', on_delete=models.SET_NULL, null=True)
    json_content = models.CharField(max_length=500, default="")
    category = models.ForeignKey('AnnotationCategory', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.json_content

######################################################################

class AnnotationContent(models.Model):
    class Meta:
        ordering = ('content',)
        verbose_name_plural = "008b. Annotations Content"

    type = models.ForeignKey('AnnotationContentType', on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=500, default="")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.content

######################################################################

class AnnotationLog(models.Model):
    class Meta:
        ordering = ('-date',)
        verbose_name_plural = "008c. Annotation Log Entries"

    annotation = models.ForeignKey('Annotation', on_delete=models.SET_NULL, null=True)
    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    char_start = models.IntegerField()
    char_end = models.IntegerField()
    #certainty = models.IntegerField()
    #certainty removed, this is surely a mistake to keep it?
    type = models.ForeignKey('AnnotationType', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('AnnotationCategory', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    #user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return str(self.annotation)

######################################################################

class AnnotationType(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "008d. Annotation Types"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class AnnotationContentType(models.Model):
    class Meta:
        ordering = ('description',)
        verbose_name_plural = "008e. Annotation Content Types"

    description = models.CharField(max_length=200, default="")
    #name = models.CharField(max_length=200, default="")
    #name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.description

######################################################################

class AnnotationCategory(models.Model):
    class Meta:
        ordering = ('parent', 'name',)
        verbose_name_plural = "008f. Annotation Categories"

    name = models.CharField(max_length=200, default="")
    parent = models.ForeignKey('AnnotationParent', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

######################################################################

class AnnotationParent(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "008g. Annotation Parents"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################
######################################################################
class NgramInWitness(models.Model):
    class Meta:
        ordering = ('-weight', '-frequency', '-nsize', 'ngram','witness')
        verbose_name_plural = "009b. Ngrams in Witnesses"
    #csvfile = models.FileField(upload_to="documents/%Y/%m/%d")
    #ngram = models.ForeignKey('Ngram', on_delete=models.SET_NULL, null=True)
    ngram = models.CharField(max_length=200, default="")
    nsize = models.IntegerField(default=0, blank=True, null=True)
    weight = models.IntegerField(default=0, blank=True, null=True)
    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    frequency = models.IntegerField(default=0, blank=True, null=True)
    #witness_dst = models.ForeignKey('Witness', related_name='witness_dst_csv', on_delete=models.SET_NULL, null=True)
######################################################################
######################################################################


class Ngram(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "009. Ngrams"
    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.name)

class Dictionary(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "010. Dictionaries"
    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.name)

######################################################################

class DictionaryEntry(models.Model):
    class Meta:
        ordering = ('entry1',)
        verbose_name_plural = "010b. Dictionary Entries"
    #name = models.CharField(max_length=200, default="")
    dictionary = models.ForeignKey('Dictionary', on_delete=models.SET_NULL, null=True)
    entry1 = models.CharField(max_length=200, default="")
    entry2 = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.entry1)

class DictionaryLine(models.Model):
    class Meta:
        ordering = ('line',)
        verbose_name_plural = "010c. Dictionary Lines"
    #name = models.CharField(max_length=200, default="")
    dictionary = models.ForeignKey('Dictionary', on_delete=models.SET_NULL, null=True)
    line = models.CharField(max_length=2000, default="")

    def __str__(self):
        return str(self.line)

######################################################################

######################################################################
######################################################################

# models merged from optools:

######################################################################

class CsvAlignment(models.Model):
    class Meta:
        ordering = ('csvlist', 'w1match')
        verbose_name_plural = "011. CSV Alignments"

    csvlist = models.ForeignKey('CsvAlignmentList', on_delete=models.SET_NULL, null=True)

    # information concerning Tibetan side
    w1match = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w1matchlength = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w1matchtarget = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w1matchfound = models.CharField(max_length=2000, default="0", blank=True, null=True)

    # information concerning Chinese side
    w2match = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w2matchlength = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w2matchtarget = models.CharField(max_length=2000, default="0", blank=True, null=True)
    w2matchfound = models.CharField(max_length=2000, default="0", blank=True, null=True)

    score = models.IntegerField(default=0, blank=True, null=True)


class CsvAlignmentList(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "011b. CSV Alignment Lists"
    name = models.CharField(max_length=200, default="noname", blank=True, null=True)
    csvfile_id = models.IntegerField(default=0, blank=True, null=True)

class UserFile(models.Model):
    class Meta:
        ordering = ('csvfile',)
        verbose_name_plural = "012. User Submitted Files"

    csvfile = models.FileField(upload_to="documents/%Y/%m/%d")
    witness_src = models.ForeignKey('Witness', related_name='witness_src_csv', on_delete=models.SET_NULL, null=True)
    witness_dst = models.ForeignKey('Witness', related_name='witness_dst_csv', on_delete=models.SET_NULL, null=True)

class UserRequest(models.Model):
    class Meta:
        ordering = ('request',)
        verbose_name_plural = "012b. User Requests"

    #username = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    #text1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    request = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    status = models.CharField(max_length=200, default="#000000", blank=True, null=True)


class UserSettings(models.Model):
    class Meta:
        ordering = ('username',)
        verbose_name_plural = "013. User Settings"

    #username = models.CharField(max_length=200, default="")
    #username = models.CharField(max_length=200, default="")
    username = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    #username = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    #user = models.CharField(max_length=200, default="")

    text1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    # text1 foreground color

    text1bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text1 background color

    text2fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text2 foreground color

    text2bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text2 background color

    text3fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text3 foreground color

    text3bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text3 background color

    text4fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text4 foreground color

    text4bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text4 background color

    mainfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #main foreground color

    mainbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #main background color

    alignmentslistfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #alignments list foreground color

    alignmentslistbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #alignments list background color

    alignmentsfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #alignment foreground color

    alignmentsbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #alignment background color

    other1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #other1 foreground color

    other1bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #other1 background color

    other2fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #other2 foreground color

    other2bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #other2 background color

    fontfamily = models.CharField(max_length=200, default="Georgia", blank=True, null=True)
    #other2 background color

    nsize1 = models.IntegerField(default=1, blank=True, null=True)
    nsize2 = models.IntegerField(default=1, blank=True, null=True)


    def __str__(self):
        return str(self.username)

######################################################################
class UserTheme(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "013b. User Themes"

    #username = models.CharField(max_length=200, default="")
    name = models.CharField(max_length=200, default="")
    #username = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    #username = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    #user = models.CharField(max_length=200, default="")

    text1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    # text1 foreground color

    text1bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text1 background color

    text2fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text2 foreground color

    text2bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text2 background color

    text3fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text3 foreground color

    text3bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text3 background color

    text4fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #text4 foreground color

    text4bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #text4 background color

    mainfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #main foreground color

    mainbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #main background color

    alignmentslistfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #alignments list foreground color

    alignmentslistbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #alignments list background color

    alignmentsfg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #alignment foreground color

    alignmentsbg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #alignment background color

    other1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #other1 foreground color

    other1bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #other1 background color

    other2fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    #other2 foreground color

    other2bg = models.CharField(max_length=200, default="#FFFFFF", blank=True, null=True)
    #other2 background color

    fontfamily = models.CharField(max_length=200, default="Georgia", blank=True, null=True)
    #other2 background color

    def __str__(self):
        return str(self.name)

######################################################################

# text1 foreground color
#text1 background color

#text2 foreground color
#text2 background color

#text3 foreground color
#text3 background color

#text4 foreground color
#text4 background color

#main foreground color
#main background color

#alignments list foreground color
#alignments list background color

#alignment foreground color
#alignment background color

#other1 foreground color
#other1 background color

#other2 foreground color
#other2 background color



######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
