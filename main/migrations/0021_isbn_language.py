# Generated by Django 2.0.3 on 2018-04-01 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20180331_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='isbn',
            name='language',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
