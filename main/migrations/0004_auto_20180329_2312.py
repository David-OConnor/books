# Generated by Django 2.0.3 on 2018-03-29 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20180328_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]