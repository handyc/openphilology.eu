# Generated by Django 2.2.2 on 2019-09-28 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('optools', '0003_sectionalignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionalignment',
            name='bleuvalue',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
