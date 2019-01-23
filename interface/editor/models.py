######################################################################

# Open Philology Database Models
# 15 June 2019

######################################################################

from django.db import models

#from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

#from django.forms import ModelForm

######################################################################

# 1 Digitiser
# 2 Language
# 3 Collection
# 4 Work
# 5 Text
# 6 Witness
# 7 WitnessIndex
# 8 WitnessPartition
# 9 WorkInCollection
# 10 Alignment
# 11 AlignmentType
# 12 AlignmentLog
# 13 Annotation
# 14 AnnotationLog
# 15 AnnotationType
# 16 AnnotationCategory
# 17 AnnotationParent
# 18 Dictionary
# 19 DictionaryEntry

######################################################################

class Digitiser(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "01. Digitisers"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Language(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "02. Languages"

    name = models.CharField(max_length=200, default="")
    iso = models.CharField(max_length=200, default="")
    bcp47 = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Collection(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "03. Collections"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Work(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "04. Works"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Text(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "05. Texts"

    name = models.CharField(max_length=200, default="")
    work = models.ForeignKey('Work', on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

######################################################################

class Witness(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "06. Witnesses"

    name = models.CharField(max_length=200, default="")
    text = models.ForeignKey('Text', on_delete=models.SET_NULL, blank=True, null=True)
    digitiser = models.ForeignKey('Digitiser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

######################################################################

class WitnessIndex(models.Model):
    class Meta:
        ordering = ('witness',)
        verbose_name_plural = "07. Witness Indexes"

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
        verbose_name_plural = "08. Witness Partitions"

    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=5000, default="")
    char_start = models.IntegerField()
    char_end = models.IntegerField()

    def __str__(self):
        return str(self.witness)

######################################################################

class WorkInCollection(models.Model):
    class Meta:
        ordering = ('number', 'collection', 'work',)
        verbose_name_plural = "09. Works in Collections"

    work = models.ForeignKey('Work', on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey('Collection', on_delete=models.SET_NULL, null=True)
    number = models.IntegerField(default=0)

    def __str__(self):
        return str(self.number) + str(self.work)

######################################################################

class Alignment(models.Model):
    class Meta:
        ordering = ('witness_src',)
        verbose_name_plural = "10. Alignments"

    witness_src = models.ForeignKey('Witness', related_name='witness_src', on_delete=models.SET_NULL, null=True)
    witness_dst = models.ForeignKey('Witness', related_name='witness_dst', on_delete=models.SET_NULL, null=True)
    char_start_src = models.IntegerField(blank=True, null=True)
    char_end_src = models.IntegerField(blank=True, null=True)
    char_start_dst = models.IntegerField(blank=True, null=True)
    char_end_dst = models.IntegerField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    type = models.ForeignKey('AlignmentType', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.witness_src)

######################################################################

class AlignmentType(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "11. Alignment Types"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class AlignmentLog(models.Model):
    class Meta:
        ordering = ('-date', 'witness_src',)
        verbose_name_plural = "12. Alignment Log Entries"

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
        verbose_name_plural = "13. Annotations"

    witness = models.ForeignKey('Witness', on_delete=models.SET_NULL, null=True)
    char_start = models.IntegerField()
    char_end = models.IntegerField()
    type = models.ForeignKey('AnnotationType', on_delete=models.SET_NULL, null=True)
    json_content = models.CharField(max_length=500, default="")
    category = models.ForeignKey('AnnotationCategory', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.json_content

######################################################################

class AnnotationLog(models.Model):
    class Meta:
        ordering = ('-date',)
        verbose_name_plural = "14. Annotation Log Entries"

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
        verbose_name_plural = "15. Annotation Types"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class AnnotationCategory(models.Model):
    class Meta:
        ordering = ('parent', 'name',)
        verbose_name_plural = "16. Annotation Categories"

    name = models.CharField(max_length=200, default="")
    parent = models.ForeignKey('AnnotationParent', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

######################################################################

class AnnotationParent(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "17. Annotation Parents"

    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name

######################################################################

class Dictionary(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "18. Dictionaries"
    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.name)

######################################################################

class DictionaryEntry(models.Model):
    class Meta:
        ordering = ('entry1',)
        verbose_name_plural = "19. Dictionary Entries"
    #name = models.CharField(max_length=200, default="")
    dictionary = models.ForeignKey('Dictionary', on_delete=models.SET_NULL, null=True)
    entry1 = models.CharField(max_length=200, default="")
    entry2 = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.entry1)

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
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
