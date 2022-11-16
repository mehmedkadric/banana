import re

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from ..scraper import PortalScraper
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from ...sentiment.lexicon_based_sentiment_analyzer import analyze
from ....models import Article, Portal
from selenium import webdriver

import datetime


class FaktorScraper(PortalScraper):
    def __init__(self, date):
        super().__init__(date)
        self.urls_demo = [
            'https://faktor.ba/podkategorija/vijesti/1#1',
        ]
        self.urls = [
            'https://faktor.ba/kategorija/bih/1',
            'https://faktor.ba/kategorija/svijet/2',
            'https://faktor.ba/kategorija/ekonomija/3',
            'https://faktor.ba/kategorija/crna-hronika/4',
            'https://faktor.ba/kategorija/sport/5',
            'https://faktor.ba/kategorija/zanimljivosti/7',
            'https://faktor.ba/kategorija/tehnomag/8',
            'https://faktor.ba/podkategorija/vijesti/1#1',
            'https://faktor.ba/podkategorija/intervjui/2#1',
            'https://faktor.ba/podkategorija/komentari/3#1',
            'https://faktor.ba/podkategorija/kultura/4#1',
            'https://faktor.ba/podkategorija/servisne-informacije/#1',
            'https://faktor.ba/podkategorija/regija/6#1',
            'https://faktor.ba/kategorija/ekonomija-promo/12#1',
            'https://faktor.ba/podkategorija/fudbal/8#1',
            'https://faktor.ba/podkategorija/kosarka/9#1',
            'https://faktor.ba/podkategorija/rukomet/10#1',
            'https://faktor.ba/podkategorija/tenis/11#1',
            'https://faktor.ba/podkategorija/ostali-sportovi/12#1'
        ]

    def run(self):
        scraped_articles = 1
        session = HTMLSession()
        set_of_articles = set([])
        articles = {}
        category = ''
        options = Options()
        options.headless = True
        try:
            for url in self.urls:
                print(url)
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.ID, 'category-button'))
                load_more_button = driver.find_element(By.ID, 'category-button')
                load_more_button.click()

                remaining_part = driver.find_element(By.ID, 'remaining-part')
                small_news = remaining_part.find_elements(By.CLASS_NAME, 'small-news')

                for small_new in small_news:
                    # Get all a-tags
                    article_url = small_new.find_element(By.TAG_NAME, 'a').get_attribute('href')

                    # Check if a-tag represents article URL
                    match = re.search(r'\d{6}$', article_url)
                    if match is not None:
                        # Continue if article URL exists in database
                        if Article.objects.filter(article_url=article_url).count() > 0:
                            # end_scraping = True
                            continue

                        # Otherwise create new 'articles' entry
                        articles[article_url] = {}
                        articles[article_url]['title'] = small_new.find_element(By.TAG_NAME, 'h2').text
                        articles[article_url]['subtitle'] = small_new.find_element(By.TAG_NAME, 'h3').text
                        articles[article_url]['category'] = url.split("kategorija/")[1].split("/")[0]

            for article in articles:
                try:
                    r = session.get(article, timeout=1)
                    html = BeautifulSoup(r.text, 'lxml')

                    articles[article]['release_date'] = self.get_release_date(html)
                    articles[article]['number_of_shares'] = int(html.find('div', {'class': 'col-8 flex-row vertical-center horizontal-end share-holder'}).text.strip())
                    articles[article]['number_of_comments'] = -1
                    articles[article]['url'] = article
                    articles[article]['portal_id'] = 2
                    articles[article]['content_lead'] = self.get_content_lead(html)
                    articles[article]['content'] = self.get_content(html)
                    articles[article]['tags'] = self.get_tags(html)
                    articles[article]['sentiment'] = analyze(articles[article]['content'])
                    articles[article]['author'] = self.get_author(html)
                    print(articles[article]['title'])
                except ValueError:
                    print("Request Timeout")
                    continue

                Article.objects.create(
                    article_portal=Portal.objects.get(id=articles[article]['portal_id']),
                    article_title=articles[article]['title'].strip(),
                    article_subtitle=articles[article]['subtitle'],
                    article_category=articles[article]['category'],
                    article_date=articles[article]['release_date'],
                    article_number_of_shares=articles[article]['number_of_shares'],
                    article_number_of_comments=articles[article]['number_of_comments'],
                    article_url=articles[article]['url'],
                    article_content=articles[article]['content'],
                    article_sentiment_bow=articles[article]['sentiment'],
                    article_tags=articles[article]['tags'],
                    article_content_lead=articles[article]['content_lead'],
                    article_author=articles[article]['author']
                )

                scraped_articles += 1
            return scraped_articles
        except ValueError:
            print(ValueError)
            pass
        return scraped_articles

    def get_release_date(self, html):
        try:
            # Example: 15.11.2022. / 18:54'
            raw_date = html.article.find_all('p')[1].text.strip()

            date = raw_date.split(" / ")[0]
            time = raw_date.split(" / ")[1]

            day = int(date.split(".")[0])
            month = int(date.split(".")[1])
            year = int(date.split(".")[2])
            hour = int(time.split(":")[0])
            min = int(time.split(":")[1])
            return datetime.datetime(year, month, day, hour, min)
        except:
            return None

    def get_content(self, html):
        content = []
        try:
            for p in html.article.find_all('p', text=True)[2:]:
                content.append(p.text.strip())
            return " ".join(content)
        except:
            return ''

    def get_content_lead(self, html):
        try:
            return html.article.find_all('p')[2].text.strip()
        except:
            return ''

    def get_tags(self, html):
        tag_list = html.find('div', {'class': 'tag-list'})
        tags = ','
        try:
            for tag in tag_list.find_all('a'):
                tags += tag.text.strip().upper() + ','
            return tags
        except:
            return ''

    def get_author(self, html):
        author = html.article.p.text.strip()
        if len(author) > 0:
            try:
                return author.replace('Autor: ', '')
            except:
                return author
        else:
            return ''




