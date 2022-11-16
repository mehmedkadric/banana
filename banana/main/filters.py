import django_filters

from .models import Article, Portal


class ArticleFilter(django_filters.FilterSet):
    article_portal = django_filters.MultipleChoiceFilter(label='Portal', field_name='article_portal',
                                                         choices=Portal.objects.all().values_list('id', 'portal_name'))
    article_title = django_filters.CharFilter(label='Title', field_name='article_title', lookup_expr='iregex')
    article_subtitle = django_filters.CharFilter(label='Subtitle', field_name='article_subtitle', lookup_expr='iregex')
    article_category = django_filters.CharFilter(label='Category', field_name='article_category', lookup_expr='iregex')
    article_tags = django_filters.CharFilter(label='Tags', field_name='article_tags', lookup_expr='iregex')
    article_number_of_shares__lt = django_filters.NumberFilter(label='Shares less than',
                                                               field_name='article_number_of_shares', lookup_expr='lt')
    article_number_of_shares__gt = django_filters.NumberFilter(label='Shares greater than',
                                                               field_name='article_number_of_shares', lookup_expr='gt')
    article_number_of_comments__lt = django_filters.NumberFilter(label='Comments less than',
                                                                 field_name='article_number_of_comments',
                                                                 lookup_expr='lt')
    article_number_of_comments__gt = django_filters.NumberFilter(label='Comments greater than',
                                                                 field_name='article_number_of_comments',
                                                                 lookup_expr='gt')
    article_date = django_filters.DateFilter(label='Date', field_name='article_date', lookup_expr='gt')

    SENTIMENT_CHOICES = (
        ('Positive', 'Positive'),
        ('Neutral', 'Neutral'),
        ('Negative', 'Negative'),
    )

    article_sentiment_bow = django_filters.MultipleChoiceFilter(label='Sentiment', field_name='article_sentiment_bow', choices=SENTIMENT_CHOICES)

    class Meta:
        model = Article
        fields = []