# Generated by Django 2.0.3 on 2018-03-31 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_gutenbergwork'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gutenbergwork',
            old_name='id',
            new_name='book_id',
        ),
    ]
