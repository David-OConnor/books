# Generated by Django 2.0.4 on 2018-04-16 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_remove_report_works'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactmessage',
            name='datetime',
            field=models.DateTimeField(default='1999-09-09'),
            preserve_default=False,
        ),
    ]
