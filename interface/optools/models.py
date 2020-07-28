# Create your models here.

from django.db import models
from django.forms import ModelForm

from django.contrib.auth import get_user_model

from editor.models import Witness

######################################################################

class CsvAlignment(models.Model):
    class Meta:
        ordering = ('csvlist', 'w1match')
        verbose_name_plural = "999. CSV Alignments"

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

class CsvAlignmentList(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "9999. CSV Alignment Lists"
    name = models.CharField(max_length=200, default="noname", blank=True, null=True)
    csvfile_id = models.IntegerField(default=0, blank=True, null=True)

class UserFile(models.Model):
    class Meta:
        ordering = ('csvfile',)
        verbose_name_plural = "99. User Submitted Files"

    csvfile = models.FileField(upload_to="documents/%Y/%m/%d")
    witness_src = models.ForeignKey('editor.Witness', related_name='witness_src_csv', on_delete=models.SET_NULL, null=True)
    witness_dst = models.ForeignKey('editor.Witness', related_name='witness_dst_csv', on_delete=models.SET_NULL, null=True)

class UserRequest(models.Model):
    class Meta:
        ordering = ('request',)
        verbose_name_plural = "99. User Requests"

    #username = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    #text1fg = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    request = models.CharField(max_length=200, default="#000000", blank=True, null=True)
    status = models.CharField(max_length=200, default="#000000", blank=True, null=True)


class UserSettings(models.Model):
    class Meta:
        ordering = ('username',)
        verbose_name_plural = "01. User Settings"

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

    def __str__(self):
        return str(self.username)

######################################################################
class UserTheme(models.Model):
    class Meta:
        ordering = ('name',)
        verbose_name_plural = "02. User Themes"

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
