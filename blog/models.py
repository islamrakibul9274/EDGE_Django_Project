from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone


class CalculatorPost(models.Model):
    CATEGORY_CHOICES = [
        ("scientific", "Scientific"),
        ("graphing", "Graphing"),
        ("financial", "Financial"),
        ("basic", "Basic"),
        ("programming", "Programming"),
    ]

    STOCK_CHOICES = [
        ("in_stock", "In stock"),
        ("low_stock", "Low stock"),
        ("out_of_stock", "Out of stock"),
        ("preorder", "Preorder"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=240, blank=True, null=True)
    description = models.TextField()
    image = models.URLField(blank=True)
    image_file = models.FileField(upload_to="calculator_images/", blank=True, null=True)
    buy_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="scientific")
    brand = models.CharField(max_length=100, default="Generic")
    stock_status = models.CharField(max_length=20, choices=STOCK_CHOICES, default="in_stock")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    affiliate_source = models.CharField(max_length=150, blank=True)
    is_featured = models.BooleanField(default=False)
    specifications = models.JSONField(default=dict, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "brand"],
                name="unique_calculator_title_brand",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.brand})"

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            discount = (self.original_price - self.price) / self.original_price * 100
            return round(discount, 1)
        return 0

    @property
    def is_new_arrival(self):
        return self.created_at >= timezone.now() - timezone.timedelta(days=30)

    @property
    def is_best_value(self):
        return self.rating >= Decimal("4.20") and (self.discount_percentage >= 10 or self.price <= 50)

    @property
    def promotional_badges(self):
        badges = []
        if self.is_featured:
            badges.append("Featured")
        if self.discount_percentage >= 15:
            badges.append("Discount")
        if self.rating >= Decimal("4.50"):
            badges.append("Top Rated")
        if self.click_count >= 10:
            badges.append("Trending")
        if self.is_new_arrival:
            badges.append("New")
        return badges

    def clean(self):
        if self.price <= 0:
            raise ValidationError({"price": "Price must be greater than zero."})

        if self.original_price is not None and self.original_price < self.price:
            raise ValidationError({"original_price": "Original price must be greater than or equal to price."})

        if self.buy_url and not self.buy_url.startswith(("http://", "https://")):
            raise ValidationError({"buy_url": "Buy URL must start with http:// or https://."})

        duplicate_qs = CalculatorPost.objects.filter(
            Q(title__iexact=self.title.strip()),
            Q(brand__iexact=self.brand.strip()),
        )
        if self.pk:
            duplicate_qs = duplicate_qs.exclude(pk=self.pk)
        if duplicate_qs.exists():
            raise ValidationError("A calculator with this title and brand already exists.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.brand}")[:220]
            slug = base_slug
            counter = 1
            while CalculatorPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"[:240]
                counter += 1
            self.slug = slug
        self.full_clean()
        super().save(*args, **kwargs)


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    calculator = models.ForeignKey(CalculatorPost, on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "calculator")

    def __str__(self):
        return f"{self.user.username} -> {self.calculator.title}"


class SavedComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_comparisons")
    name = models.CharField(max_length=120)
    calculators = models.ManyToManyField(CalculatorPost, related_name="comparison_sets")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="price_alerts")
    calculator = models.ForeignKey(CalculatorPost, on_delete=models.CASCADE, related_name="price_alerts")
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "calculator", "target_price")

    def __str__(self):
        return f"{self.user.username} alert for {self.calculator.title} at {self.target_price}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calculator_reviews")
    calculator = models.ForeignKey(CalculatorPost, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "calculator")

    def __str__(self):
        return f"{self.calculator.title} review by {self.user.username}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class BackInStockSubscription(models.Model):
    email = models.EmailField()
    calculator = models.ForeignKey(CalculatorPost, on_delete=models.CASCADE, related_name="stock_subscriptions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("email", "calculator")

    def __str__(self):
        return f"{self.email} -> {self.calculator.title}"


class AffiliateClick(models.Model):
    calculator = models.ForeignKey(CalculatorPost, on_delete=models.CASCADE, related_name="affiliate_clicks")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=120, blank=True)
    page = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Click: {self.calculator.title}"


class Article(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(unique=True, max_length=240, blank=True)
    summary = models.TextField()
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    og_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:230]
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"[:240]
                counter += 1
            self.slug = slug
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
