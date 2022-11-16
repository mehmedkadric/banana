import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Article
from django.forms import ModelForm

from .models import Portal


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = None

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class DataPreviewFilterForm(forms.Form):
    article_title = forms.CharField(label='Article Title', max_length=200, empty_value="", required=False)
    article_subtitle = forms.CharField(label='Article Subtitle', max_length=200, empty_value="", required=False)
    article_sentiment = forms.CharField(label='Article Sentiment', max_length=20, empty_value="", required=False)
    article_nos = forms.IntegerField(label='Min shares', required=False)
    article_noc = forms.IntegerField(label='Min comments', required=False)
    article_tags = forms.CharField(label='Article Tag', max_length=200, empty_value="", required=False,
                                   widget=forms.TextInput(attrs={'class': 'autocomplete'}))


class CommentsFilterForm(forms.Form):
    SENTIMENT_CHOICES = (
        ("Positive", "Positive"),
        ("Neutral", "Neutral"),
        ("Negative", "Negative"),
    )
    comment_username = forms.CharField(label='Username', max_length=200, empty_value="", required=False)
    comment_content = forms.CharField(label='Comment', max_length=200, empty_value="", required=False)
    comment_sentiment = forms.MultipleChoiceField(choices=SENTIMENT_CHOICES, label='Comment Sentiment', required=False)


class GetMoreDataForm(forms.Form):
    from_date = forms.DateField(widget=forms.SelectDateWidget(),
                                label='From Date',
                                initial=datetime.date.today().strftime("%Y-%m-%d"))
    portals = [(portal.portal_name, portal.portal_name) for portal in Portal.objects.all()]

    selected_portals = forms.MultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        choices=portals,
        label='',
    )
