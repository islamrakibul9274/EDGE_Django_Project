from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from blog.sitemaps import ArticleSitemap, CalculatorSitemap, StaticViewSitemap
from blog.views import (
    ai_assistant,
    add_price_alert,
    article_detail,
    article_list,
    buy_now_redirect,
    calculator_detail,
    calculator_list,
    compare_calculators,
    handler404,
    handler500,
    home,
    recommender_quiz,
    register,
    robots_txt,
    save_comparison,
    submit_review,
    subscribe_back_in_stock,
    subscribe_newsletter,
    toggle_wishlist,
)

sitemaps = {
    "static": StaticViewSitemap,
    "calculators": CalculatorSitemap,
    "articles": ArticleSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("catalog/", calculator_list, name="calculator_list"),
    path("blog/", calculator_list),
    path("calculator/<slug:slug>/", calculator_detail, name="calculator_detail"),
    path("calculator/<slug:slug>/buy/", buy_now_redirect, name="buy_now_redirect"),
    path("calculator/<slug:slug>/wishlist/", toggle_wishlist, name="toggle_wishlist"),
    path("calculator/<slug:slug>/price-alert/", add_price_alert, name="add_price_alert"),
    path("calculator/<slug:slug>/review/", submit_review, name="submit_review"),
    path("calculator/<slug:slug>/back-in-stock/", subscribe_back_in_stock, name="subscribe_back_in_stock"),
    path("compare/", compare_calculators, name="compare_calculators"),
    path("compare/save/", save_comparison, name="save_comparison"),
    path("newsletter/subscribe/", subscribe_newsletter, name="subscribe_newsletter"),
    path("articles/", article_list, name="article_list"),
    path("articles/<slug:slug>/", article_detail, name="article_detail"),
    path("quiz/", recommender_quiz, name="recommender_quiz"),
    path("assistant/", ai_assistant, name="ai_assistant"),
    path("accounts/register/", register, name="register"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]

handler404 = handler404
handler500 = handler500

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
