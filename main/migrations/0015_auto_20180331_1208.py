# Generated by Django 2.0.3 on 2018-03-31 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20180331_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adelaidework',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]