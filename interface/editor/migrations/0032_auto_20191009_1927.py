# Generated by Django 2.1.3 on 2019-10-09 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0031_auto_20191009_1924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alignment',
            name='char_end_dst',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignment',
            name='char_end_src',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignment',
            name='char_start_dst',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignment',
            name='char_start_src',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignment',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignmentlog',
            name='char_end_src',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignmentlog',
            name='char_start_dst',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alignmentlog',
            name='char_start_src',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
