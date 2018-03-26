# Generated by Django 2.0.3 on 2018-03-26 16:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20180326_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='categories',
            field=models.CharField(blank=True, choices=[(0, 'information'), (2, 'free downloads'), (3, 'purchases')], max_length=50, null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
        migrations.AlterField(
            model_name='work',
            name='genre',
            field=models.CharField(blank=True, choices=[(0, 'sci-fi'), (1, 'romance'), (2, 'non-fiction'), (3, 'science'), (4, 'language'), (5, 'philosophy'), (6, 'comedy'), (7, 'satire'), (8, 'OCA'), (9, 'SCAR'), (10, 'OCF'), (11, 'Red air')], max_length=50, null=True, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
        migrations.AlterField(
            model_name='work',
            name='publication_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_sources', to='main.Source'),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_sources', to='main.Work'),
        ),
    ]
