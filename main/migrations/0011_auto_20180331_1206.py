# Generated by Django 2.0.3 on 2018-03-31 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20180331_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adelaidework',
            name='title',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='adelaidework',
            name='translator',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
