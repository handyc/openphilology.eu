# Generated by Django 2.1.3 on 2019-06-16 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0005_auto_20190616_1156'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workincollection',
            options={'ordering': ('collection',), 'verbose_name_plural': '08. Works in Collection'},
        ),
        migrations.RemoveField(
            model_name='workincollection',
            name='number',
        ),
    ]
