from django.db import models


# Create your models here.
class Portal(models.Model):
    portal_name = models.CharField(max_length=200)
    portal_slug = models.CharField(max_length=20)
    portal_url = models.URLField(max_length=200)
    portal_publisher = models.CharField(max_length=200, blank=True, default='')
    portal_director = models.CharField(max_length=200, blank=True, default='')
    portal_editor_in_chief = models.CharField(max_length=200, blank=True, default='')
    portal_about_us = models.TextField()
    portal_logo = models.ImageField(upload_to='images/', blank=True, default='')

    class Meta:
        verbose_name_plural = "Portals"

    def __str__(self):
        return self.portal_name


class Article(models.Model):
    article_portal = models.ForeignKey(Portal, on_delete=models.CASCADE)
    article_title = models.CharField(max_length=255)
    article_subtitle = models.CharField(max_length=255)
    article_category = models.CharField(max_length=255)
    article_release_date = models.CharField(max_length=255)
    article_url = models.URLField(max_length=200)
    article_content = models.TextField(blank=True, default='')
    article_sentiment_bow = models.CharField(max_length=200, blank=True, default='')
    article_tags = models.CharField(max_length=200, blank=True, default='')
    article_content_lead = models.TextField(blank=True, default='')
    article_number_of_shares = models.IntegerField(default=-1)
    article_number_of_comments = models.IntegerField(default=-1)
    article_date = models.DateTimeField(null=True, blank=True)
    article_author = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.article_title


class Comment(models.Model):
    comment_username = models.CharField(max_length=200)
    comment_content = models.TextField(blank=True, default='')
    comment_like_count = models.IntegerField(default=0)
    comment_dislike_count = models.IntegerField(default=0)
    comment_url = models.URLField(max_length=255)
    comment_sentiment_bow = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.article_title
