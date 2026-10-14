from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Article, CalculatorPost


class StaticViewSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return ["home", "calculator_list", "article_list", "recommender_quiz", "ai_assistant"]

    def location(self, item):
        return reverse(item)


class CalculatorSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return CalculatorPost.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
