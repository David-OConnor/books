# Generated by Django 2.0.3 on 2018-03-31 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20180330_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='translator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='main.Author'),
        ),
        migrations.AlterField(
            model_name='work',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='works', to='main.Author'),
        ),
    ]
