import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import (
    AffiliateClick,
    Article,
    BackInStockSubscription,
    CalculatorPost,
    NewsletterSubscription,
    PriceAlert,
    Review,
    SavedComparison,
    WishlistItem,
)


def export_calculators_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="calculators.csv"'
    writer = csv.writer(response)
    writer.writerow(["Title", "Brand", "Category", "Price", "Rating", "Stock Status", "Affiliate Source"])
    for item in queryset:
        writer.writerow([item.title, item.brand, item.category, item.price, item.rating, item.stock_status, item.affiliate_source])
    return response


def mark_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


@admin.register(CalculatorPost)
class CalculatorPostAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "category", "price", "rating", "stock_status", "is_featured", "click_count")
    list_filter = ("category", "stock_status", "is_featured", "brand")
    search_fields = ("title", "brand", "description", "affiliate_source")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("click_count", "created_at", "updated_at")
    actions = [export_calculators_csv, mark_featured]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("calculator", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("calculator__title", "user__username", "title", "comment")
    actions = ["approve_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(AffiliateClick)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ("calculator", "source", "page", "user", "created_at")
    list_filter = ("source", "page", "created_at")
    search_fields = ("calculator__title", "source", "page", "user__username")
    date_hierarchy = "created_at"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "updated_at")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "summary", "body", "seo_title", "seo_description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email",)


@admin.register(BackInStockSubscription)
class BackInStockSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "calculator", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email", "calculator__title")


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ("user", "calculator", "target_price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "calculator__title")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "calculator", "created_at")
    search_fields = ("user__username", "calculator__title")


@admin.register(SavedComparison)
class SavedComparisonAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "calculator_count")
    search_fields = ("name", "user__username")

    def calculator_count(self, obj):
        return obj.calculators.count()
