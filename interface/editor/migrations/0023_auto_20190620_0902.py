# Generated by Django 2.2.2 on 2019-06-20 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0022_witnessfile_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='witness',
            name='text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='editor.Text'),
        ),
    ]
