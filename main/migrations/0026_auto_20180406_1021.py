# Generated by Django 2.0.3 on 2018-04-06 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20180403_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gutenbergwork',
            name='translator',
        ),
        migrations.AddField(
            model_name='gutenbergwork',
            name='editor',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='gutenbergwork',
            name='illustrator',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='gutenbergwork',
            name='subtitle',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]