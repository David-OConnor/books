# Generated by Django 2.0.3 on 2018-03-31 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20180331_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='work',
            name='publication_date',
        ),
    ]