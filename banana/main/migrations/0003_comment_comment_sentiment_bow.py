# Generated by Django 3.2.13 on 2022-10-26 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_article_portal'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_sentiment_bow',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
