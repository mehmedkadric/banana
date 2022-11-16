# Generated by Django 3.2.13 on 2022-10-26 12:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment_username', models.CharField(max_length=200)),
                ('comment_content', models.TextField(blank=True, default='')),
                ('comment_like_count', models.IntegerField(default=0)),
                ('comment_dislike_count', models.IntegerField(default=0)),
                ('comment_url', models.URLField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Comments',
            },
        ),
    ]