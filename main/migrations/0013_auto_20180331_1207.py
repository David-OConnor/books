# Generated by Django 2.0.3 on 2018-03-31 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20180331_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adelaidework',
            name='author_first',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='adelaidework',
            name='author_last',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='adelaidework',
            name='url',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]