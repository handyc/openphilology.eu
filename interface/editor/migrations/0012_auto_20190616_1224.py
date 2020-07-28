# Generated by Django 2.2.2 on 2019-06-16 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0011_auto_20190616_1220'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='annotation',
            options={'ordering': ('witness', 'char_start'), 'verbose_name_plural': '12. Annotations'},
        ),
        migrations.AddField(
            model_name='annotationcategory',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='editor.AnnotationParent'),
        ),
    ]
