# Generated by Django 2.0.3 on 2018-04-07 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20180406_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worksource',
            name='book_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='epub_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='kindle_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='pdf_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='worksource',
            name='purchase_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]