# Generated by Django 3.2.13 on 2022-11-15 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20221112_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='article_author',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]