# Generated by Django 2.2.2 on 2019-06-16 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0019_auto_20190616_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alignmentlog',
            options={'ordering': ('-date', 'witness_src'), 'verbose_name_plural': '11. Alignment Log Entries'},
        ),
        migrations.AlterModelOptions(
            name='annotationlog',
            options={'ordering': ('-date', 'score'), 'verbose_name_plural': '13. Annotation Log Entries'},
        ),
    ]
