# Generated by Django 2.2.2 on 2019-06-15 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('iso', models.CharField(default='', max_length=200)),
                ('bcp47', models.CharField(default='', max_length=200)),
            ],
            options={
                'verbose_name_plural': '01. Languages',
                'ordering': ('name',),
            },
        ),
    ]
