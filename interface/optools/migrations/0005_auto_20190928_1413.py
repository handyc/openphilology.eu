# Generated by Django 2.2.2 on 2019-09-28 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('optools', '0004_auto_20190928_1339'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ('witness', 'number'), 'verbose_name_plural': 'Sections'},
        ),
    ]
