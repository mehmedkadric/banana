import datetime, time
import json
from collections import Counter
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .filters import ArticleFilter
from .src.portals.klix.KlixScraper import KlixScraper
from .src.portals.faktor.FaktorScraper import FaktorScraper
from .forms import NewUserForm, DataPreviewFilterForm, CommentsFilterForm, GetMoreDataForm

# Create your views here.
from .models import Portal, Article, Comment
from .src.sentiment.lexicon_based_sentiment_analyzer import analyze


def landing_page(request):
    messages.info(request, "Please login or register")
    return render(request, 'main/main_landing.html')


@login_required(login_url='/landing/')
def about_us(request):
    return render(request, 'main/about_us.html')


@login_required(login_url='/landing/')
def homepage(request):
    return render(request=request,
                  template_name="main/main_portals.html",
                  context={"portals": Portal.objects.all})


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = NewUserForm
    return render(request, "main/register.html", context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {username}!")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    if request.user.is_authenticated:
        messages.info(request, "Already logged in")
        return redirect("main:homepage")
    form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})


@login_required(login_url='/landing/')
def profile(request):
    return render(request=request, template_name="main/profile.html")


@login_required(login_url='/portals/<slug:slug>/')
def portal_about(request, slug):
    slugs = [s.portal_slug for s in Portal.objects.all()]
    if slug in slugs:
        portal = Portal.objects.filter(portal_slug=slug).first()
        from django.db.models.functions import TruncDay
        articles = Article.objects.all()\
            .annotate(date=TruncDay('article_date'))\
            .values('date') \
            .annotate(created_count=Count('id'))\
            .order_by('date')


        article_count = Article.objects.filter(article_portal_id=portal.id).count()

        categories = Article.objects.filter(article_portal_id=portal.id).values('article_category').annotate(total=Count('article_category')).filter(total__gt=0.1*article_count).order_by('-total')
        article_total = [l['total'] for l in categories]
        article_category = [d['article_category'] for d in categories]

        raw_tags = Article.objects.filter(article_portal_id=portal.id).values('article_tags')
        tags = []
        for tag in raw_tags:
            temp = tag['article_tags'].split(',')
            for t in temp:
                if t != '':
                    tags.append(t)

        tags_count = Counter(tags).most_common(20)

        tag_labels = [t[0] for t in tags_count]
        tag_data = [t[1] for t in tags_count]

        data = {
            "category_labels": article_category,
            "category_data": article_total,
            "tag_labels": tag_labels,
            "tag_data": tag_data
        }

        for a in articles:
            a['date'] = int(time.mktime(a['date'].timetuple())) * 1000

        return render(request=request,
                      template_name="main/portal_about.html",
                      context={"portal": portal, "data": data})
    else:
        return redirect("main:homepage")


@login_required(login_url='/gmd/')
def get_more_data(request):
    if request.is_ajax and request.method == 'POST':
        scraped_articles = 0
        form = GetMoreDataForm(request.POST)
        if form.is_valid():
            selected_portals = request.POST.getlist('selected_portals')
            unsupported_portals = []
            for p in selected_portals:
                if p == "Klix.ba":
                    klix_scraper = KlixScraper(form.cleaned_data['from_date'])
                    scraped_articles += klix_scraper.run()
                elif p == "Faktor.ba":
                    faktor_scraper = FaktorScraper(form.cleaned_data['from_date'])
                    scraped_articles += faktor_scraper.run()
                elif p == "Dnevni avaz":
                    unsupported_portals.append("Dnevni avaz")
                else:
                    pass
            msg = ", ".join(unsupported_portals)
            if len(unsupported_portals) == 1:
                msg = "Unsupported portal: " + msg
            elif len(unsupported_portals) > 1:
                msg = "Unsupported portals: " + msg
            else:
                msg = ""
            return JsonResponse({'success': True, 'scraped_articles': scraped_articles, 'msg': msg})
    form = GetMoreDataForm()
    return render(request, 'gmd/choose_source.html', {'form': form})


@login_required(login_url='/data/')
def preview_data(request):
    context = {}

    filtered_articles = ArticleFilter(
        request.GET,
        # queryset=Article.objects.distinct('article_category')
        queryset=Article.objects.all().order_by('-article_date'),
    )

    context['filtered_articles'] = filtered_articles

    paginated_filtered_articles = Paginator(filtered_articles.qs, 5)
    page_number = 1
    if request.GET.get('page', 1) != "…":
        page_number = request.GET.get('page', 1)
    article_page_object = paginated_filtered_articles.get_page(page_number)

    context['article_page_object'] = article_page_object
    context['page_range'] = paginated_filtered_articles.get_elided_page_range(number=page_number)

    return render(request, 'data/preview_data.html', context=context)

    """
    # Get distinct tags
    raw_tags = Article.objects.order_by().values('article_tags').distinct()
    tags = {}
    for tag in raw_tags:
        temp = tag['article_tags'].split(',')
        for t in temp:
            if t != '':
                tags[t] = None

    # if a GET (or any other method) we'll create a blank form
    if not request.method == 'POST':
        form = DataPreviewFilterForm()
        articles = Article.objects.get_queryset().order_by('-article_date')
        i = 1
        #for a in articles:
        #    print(i)
        #    a.article_sentiment_bow = analyze(a.article_content)
        #    a.save()
        #    i = i + 1
        paginator = Paginator(articles, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number)

        return render(request, 'data/preview_data.html', context={"articles": page_obj,
                                                                  "page_range": page_range,
                                                                  "form": form,
                                                                  "tags": json.dumps(tags)})
    # if this is a POST request we need to process the form data
    else:
        # create a form instance and populate it with data from the request:
        form = DataPreviewFilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            article_title = form.cleaned_data['article_title']
            article_subtitle = form.cleaned_data['article_subtitle']
            article_sentiment = form.cleaned_data['article_sentiment']
            article_noc = form.cleaned_data['article_noc']
            article_nos = form.cleaned_data['article_nos']
            article_tags = "," + form.cleaned_data['article_tags'] + ","

            if article_noc is None:
                article_noc = 0

            if article_nos is None:
                article_nos = 0

            articles = Article.objects\
                .filter(article_title__icontains=article_title)\
                .filter(article_subtitle__icontains=article_subtitle)\
                .filter(article_sentiment_bow__icontains=article_sentiment)\
                .filter(article_number_of_comments__gte=article_noc)\
                .filter(article_number_of_shares__gte=article_nos)\
                .filter(article_tags__contains=article_tags)\
                .order_by('-article_date')

            paginator = Paginator(articles, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            page_range = paginator.get_elided_page_range(number=page_number)
            return render(request, 'data/preview_data.html', context={"articles": page_obj,
                                                                      "page_range": page_range,
                                                                      "form": form,
                                                                      "tags": tags})
    """

@login_required(login_url='/comment/')
def comment(request):
    if request.is_ajax():
        text = request.GET.get('text')
        return JsonResponse({'class': analyze(text)})
    return render(request, 'data/comment.html')


@login_required(login_url='/comments/')
def comments(request):
    # if a GET (or any other method) we'll create a blank form
    if not request.method == 'POST':
        form = CommentsFilterForm()
        comments_raw = Comment.objects.all().order_by('-comment_dislike_count')
        i = 1
        #for c in comments_raw:
        #   print(i)
        #   c.comment_sentiment_bow = analyze(c.comment_content)
        #   c.save()
        #   i = i + 1
        paginator = Paginator(comments_raw, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number)

        return render(request, 'data/comments.html', context={"comments": page_obj,
                                                              "page_range": page_range,
                                                              "form": form})
    # if this is a POST request we need to process the form data
    else:
        # create a form instance and populate it with data from the request:
        form = CommentsFilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            comment_username = form.cleaned_data['comment_username']
            comment_content = form.cleaned_data['comment_content']
            comment_sentiment = form.cleaned_data['comment_sentiment']
            if comment_sentiment is not None and len(comment_sentiment) == 0:
                comment_sentiment = ["Positive", "Negative", "Neutral"]

            comments_raw = Comment.objects \
                .filter(comment_username__iregex=r"" + comment_username + "") \
                .filter(comment_content__iregex=r"" + comment_content + "") \
                .filter(comment_sentiment_bow__in=comment_sentiment) \
                .order_by('-comment_dislike_count')

            paginator = Paginator(comments_raw, 10)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            page_range = paginator.get_elided_page_range(number=page_number)
            return render(request, 'data/comments.html', context={"comments": page_obj,
                                                                  "page_range": page_range,
                                                                  "form": form})


@login_required(login_url='/filter/')
def filter_news(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DataPreviewFilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            article_title = form.cleaned_data['article_title']
            article_subtitle = form.cleaned_data['article_subtitle']

            return HttpResponseRedirect('/data/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DataPreviewFilterForm()

    return render(request, 'landing.html', {'form': form})
