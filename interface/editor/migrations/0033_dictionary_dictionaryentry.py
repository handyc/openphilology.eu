# Generated by Django 2.1.3 on 2019-10-22 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0032_auto_20191009_1927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
            ],
            options={
                'verbose_name_plural': '18. Dictionaries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='DictionaryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
            ],
            options={
                'verbose_name_plural': '19. Dictionary Entries',
                'ordering': ('name',),
            },
        ),
    ]
