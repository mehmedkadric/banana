# Generated by Django 3.2.13 on 2022-11-11 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20221111_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='article_number_of_shares',
            field=models.IntegerField(default=-1),
        ),
    ]
