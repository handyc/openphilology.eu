# Generated by Django 2.2.2 on 2019-06-16 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0013_auto_20190616_1248'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='annotationcategory',
            options={'ordering': ('parent', 'name'), 'verbose_name_plural': '15. Annotation Categories'},
        ),
    ]
