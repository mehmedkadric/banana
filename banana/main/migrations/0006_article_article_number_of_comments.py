# Generated by Django 3.2.13 on 2022-11-11 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_article_article_number_of_shares'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='article_number_of_comments',
            field=models.IntegerField(default=-1),
        ),
    ]