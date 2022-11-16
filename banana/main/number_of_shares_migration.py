from models import Article
articles = Article.objects.all()
for article in articles:
    cnt = 0
    try:
        article.article_number_of_shares = int(article.article_shares_no)
        article.save()
    except:
        cnt += 1
        print(cnt)
