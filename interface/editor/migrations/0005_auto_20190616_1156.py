# Generated by Django 2.1.3 on 2019-06-16 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0004_auto_20190616_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workincollection',
            name='number',
            field=models.IntegerField(),
        ),
    ]
