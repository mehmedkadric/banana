from ..scraper import PortalScraper
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from ...sentiment.lexicon_based_sentiment_analyzer import analyze
from ....models import Article, Portal
import datetime


class KlixScraper(PortalScraper):
    def __init__(self, date):
        super().__init__(date)
        self.urls_demo = [
            'https://www.klix.ba/sport/rukomet?str=',
            'https://www.klix.ba/auto/tuning?str=',
            'https://www.klix.ba/vijesti/humanitarne-akcije?str=',
            'https://www.klix.ba/sport/formula1?str='
        ]
        self.urls = [
            'https://www.klix.ba/vijesti/bih?str=',
            'https://www.klix.ba/vijesti/regija?str=',
            'https://www.klix.ba/vijesti/svijet?str=',
            'https://www.klix.ba/vijesti/dijaspora?str=',
            'https://www.klix.ba/vijesti/crna-hronika?str=',
            'https://www.klix.ba/vijesti/humanitarne-akcije?str=',
            'https://www.klix.ba/vijesti?str=',
            'https://www.klix.ba/biznis/privreda?str=',
            'https://www.klix.ba/biznis/finansije?str=',
            'https://www.klix.ba/biznis/investicije?str=',
            'https://www.klix.ba/biznis/smart-cash?str=',
            'https://www.klix.ba/biznis/berza?str=',
            'https://www.klix.ba/biznis/startupi?str=',
            'https://www.klix.ba/biznis/posao?str=',
            'https://www.klix.ba/biznis?str=',
            'https://www.klix.ba/sport/nogomet?str=',
            'https://www.klix.ba/sport/kosarka?str=',
            'https://www.klix.ba/sport/tenis?str=',
            'https://www.klix.ba/sport/rukomet?str=',
            'https://www.klix.ba/sport/formula1?str=',
            'https://www.klix.ba/sport/skijanje?str=',
            'https://www.klix.ba/sport/atletika?str=',
            'https://www.klix.ba/sport/borilacki-sportovi?str=',
            'https://www.klix.ba/sport/plivanje?str=',
            'https://www.klix.ba/sport?str=',
            'https://www.klix.ba/magazin/kultura?str=',
            'https://www.klix.ba/magazin/muzika?str=',
            'https://www.klix.ba/magazin/film-tv?str=',
            'https://www.klix.ba/magazin/showbiz?str=',
            'https://www.klix.ba/magazin/zanimljivosti?str=',
            'https://www.klix.ba/magazin?str=',
            'https://www.klix.ba/lifestyle/modailjepota?str=',
            'https://www.klix.ba/lifestyle/zdravlje?str=',
            'https://www.klix.ba/lifestyle/vezeiseks?str=',
            'https://www.klix.ba/lifestyle/gastro?str=',
            'https://www.klix.ba/lifestyle/kucaiured?str=',
            'https://www.klix.ba/lifestyle/putovanja?str=',
            'https://www.klix.ba/lifestyle/bebe?str=',
            'https://www.klix.ba/lifestyle/fitness?str=',
            'https://www.klix.ba/lifestyle/ljubimci?str=',
            'https://www.klix.ba/lifestyle?str=',
            'https://www.klix.ba/scitech/nauka?str=',
            'https://www.klix.ba/scitech/tehnologija?str=',
            'https://www.klix.ba/scitech?str=',
            'https://www.klix.ba/auto/testovi?str=',
            'https://www.klix.ba/auto/noviteti?str=',
            'https://www.klix.ba/auto/koncepti?str=',
            'https://www.klix.ba/auto/tuning?str='
        ]

    def run(self):
        scraped_articles = 0
        session = HTMLSession()
        try:
            page_number = 0
            for url in self.urls:
                while True:
                    end_scraping = False
                    page = session.get(url+str(page_number))
                    page_number += 1
                    soup = BeautifulSoup(page.text, 'lxml', from_encoding='utf-16')

                    # Break if there is no more pages
                    if soup.find('div', {'class': 'px-3 py-28 md:px-4 xl:px-2 md:py-32 text-center'}) is not None:
                        break

                    articles_urls = []
                    for article in soup.find_all('article'):
                        articles_urls.append('https://www.klix.ba' + article.a['href'])

                    for article_url in articles_urls:

                        print("/".join(article_url.split("/")[3:-2]) + ", page no: " + str(page_number))
                        # Stop scraping if the article has already been scraped
                        if Article.objects.filter(article_url=article_url).count() > 0:
                            end_scraping = True
                            break

                        article_html = session.get(article_url)
                        article_soup = BeautifulSoup(article_html.text, 'lxml', from_encoding='utf-16')

                        article_items = {
                            'title': article_soup.h1.text.replace("\n", "").strip(),
                            'subtitle': article_soup.find('article').find("div", {'class': 'flex items-center'}).find('div').text.strip(),
                            'category': "/".join(article_url.split("/")[3:-2]),
                            'release_date': self.get_release_date(article_soup),
                            'number_of_shares': self.get_number_of_shares(article_soup),
                            'number_of_comments': self.get_number_of_comments(article_soup),
                            'url': article_url,
                            'portal_id': 1,
                            'content_lead': article_soup.find('p', {'class': 'lead'}).text.strip(),
                            'content': self.get_content(article_soup),
                            'tags': self.get_tags(article_soup),
                            'sentiment': analyze(self.get_content(article_soup)),
                            'author': self.get_author(article_soup)
                        }
                        print(scraped_articles)
                        print(article_items['category'] + ", page no: " + str(page_number))
                        print(article_items['title'])


                        Article.objects.create(
                            article_portal=Portal.objects.get(id=article_items['portal_id']),
                            article_title=article_items['title'].strip(),
                            article_subtitle=article_items['subtitle'],
                            article_category=article_items['category'],
                            article_date=article_items['release_date'],
                            article_number_of_shares=article_items['number_of_shares'],
                            article_number_of_comments=article_items['number_of_comments'],
                            article_url=article_items['url'],
                            article_content=article_items['content'],
                            article_sentiment_bow=article_items['sentiment'],
                            article_tags=article_items['tags'],
                            article_content_lead=article_items['content_lead'],
                            article_author=article_items['author']
                        )
                        scraped_articles += 1
                    if end_scraping:
                        break

        except ValueError:
            print(ValueError)
            raise Exception("Something went wrong.")
        return scraped_articles

    def get_number_of_shares(self, article_soup):
        shares = article_soup.find_all('div', {'class': 'w-1/2'})[1].find('div').text
        try:
            val = 1.0
            if "k" in shares:
                val = float(shares.replace("k", "")) * 1000.0
                return int(val)
            else:
                return int(shares)
        except:
            return -1

    def get_number_of_comments(self, article_soup):
        comments = article_soup.find_all('div', {'class': 'w-1/2'})[0].find('div').text
        try:
            val = 1.0
            if "k" in comments:
                val = float(comments.replace("k", "")) * 1000.0
                return int(val)
            else:
                return int(comments)
        except:
            return -1

    def get_content(self, article_soup):
        try:
            content = article_soup.find('p', {'class': 'lead'}).text
            for p in article_soup.find_all('p'):
                if not p.has_attr('style') and not p.has_attr('class'):
                    content += " " + p.text.replace("\n", "")
            return content.strip()
        except:
            return ""

    def get_tags(self, article_soup):
        try:
            tags = ","
            for tag in article_soup.find('div', {'class': 'scrollbar-none'}).find_all('a'):
                tags += tag.text.upper() + ','
            return tags
        except:
            return ""

    def get_release_date(self, article_soup):
        r_date = article_soup.find('div', {'class': 'text-sm text-gray-500 dark:text-gray-300'}).span['title'].strip()
        date = r_date.split(" u ")[0]
        time = r_date.split(" u ")[1]

        day = int(date.split(".")[0])
        month = int(date.split(".")[1])
        year = int(date.split(".")[2])
        hour = int(time.split(":")[0])
        min = int(time.split(":")[1])
        return datetime.datetime(year, month, day, hour, min)

    def get_author(self, article_soup):
        try:
            author = article_soup.find('div', {'class': 'font-semibold text-tiny mb-1 leading-tight dark:text-white'}).text.strip()
            return author
        except:
            return ''
