from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BackInStockForm, NewsletterForm, PriceAlertForm, RegisterForm, ReviewForm
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


SORT_OPTIONS = {
    "newest": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "rating": "-rating",
    "trending": "-click_count",
}


def home(request):
    featured = CalculatorPost.objects.filter(is_featured=True)[:6]
    new_arrivals = CalculatorPost.objects.order_by("-created_at")[:6]
    best_value = CalculatorPost.objects.order_by("-rating", "price")[:6]

    context = {
        "featured": featured,
        "new_arrivals": new_arrivals,
        "best_value": [item for item in best_value if item.is_best_value][:6] or best_value,
        "seo_title": "Calculator Store | Find the Best Calculator",
        "seo_description": "Shop and compare scientific, graphing, and financial calculators.",
    }
    return render(request, "index.html", context)


def calculator_list(request):
    calculators = CalculatorPost.objects.all()

    query = request.GET.get("q", "").strip()
    brand = request.GET.get("brand", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if query:
        calculators = calculators.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__icontains=query)
            | Q(affiliate_source__icontains=query)
        )

    if brand:
        calculators = calculators.filter(brand__iexact=brand)

    if category:
        calculators = calculators.filter(category=category)

    if min_price:
        try:
            calculators = calculators.filter(price__gte=Decimal(min_price))
        except Exception:
            messages.warning(request, "Invalid minimum price ignored.")

    if max_price:
        try:
            calculators = calculators.filter(price__lte=Decimal(max_price))
        except Exception:
            messages.warning(request, "Invalid maximum price ignored.")

    order_by = SORT_OPTIONS.get(sort, "-created_at")
    calculators = calculators.order_by(order_by)

    paginator = Paginator(calculators, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    brands = CalculatorPost.objects.order_by("brand").values_list("brand", flat=True).distinct()

    context = {
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "brands": brands,
        "categories": CalculatorPost.CATEGORY_CHOICES,
        "selected": {
            "q": query,
            "brand": brand,
            "category": category,
            "sort": sort,
            "min_price": min_price,
            "max_price": max_price,
        },
        "seo_title": "Calculator Catalog | Calculator Store",
        "seo_description": "Search, filter, and compare the latest calculators.",
    }
    return render(request, "blog.html", context)


def calculator_detail(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    approved_reviews = calculator.reviews.filter(is_approved=True)
    review_form = ReviewForm()
    alert_form = PriceAlertForm()
    stock_form = BackInStockForm(initial={"email": request.user.email if request.user.is_authenticated else ""})

    related = (
        CalculatorPost.objects.filter(category=calculator.category)
        .exclude(pk=calculator.pk)
        .order_by("-rating", "price")[:4]
    )

    context = {
        "calculator": calculator,
        "related_calculators": related,
        "reviews": approved_reviews,
        "review_form": review_form,
        "alert_form": alert_form,
        "stock_form": stock_form,
        "seo_title": calculator.title,
        "seo_description": calculator.description[:150],
        "og_image": calculator.image,
    }
    return render(request, "calculator_detail.html", context)


@login_required
def toggle_wishlist(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    item, created = WishlistItem.objects.get_or_create(user=request.user, calculator=calculator)
    if not created:
        item.delete()
        messages.success(request, "Removed from wishlist.")
    else:
        messages.success(request, "Added to wishlist.")
    return redirect("calculator_detail", slug=slug)


@login_required
def add_price_alert(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    if request.method == "POST":
        form = PriceAlertForm(request.POST)
        if form.is_valid():
            PriceAlert.objects.get_or_create(
                user=request.user,
                calculator=calculator,
                target_price=form.cleaned_data["target_price"],
            )
            messages.success(request, "Price alert saved.")
        else:
            messages.error(request, "Could not save price alert.")
    return redirect("calculator_detail", slug=slug)


def subscribe_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            NewsletterSubscription.objects.get_or_create(email=form.cleaned_data["email"])
            messages.success(request, "Subscribed to newsletter.")
        else:
            messages.error(request, "Invalid email address.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


def subscribe_back_in_stock(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    if request.method == "POST":
        form = BackInStockForm(request.POST)
        if form.is_valid():
            BackInStockSubscription.objects.get_or_create(
                email=form.cleaned_data["email"],
                calculator=calculator,
            )
            messages.success(request, "You will be notified when this is back in stock.")
        else:
            messages.error(request, "Invalid email address.")
    return redirect("calculator_detail", slug=slug)


@login_required
def submit_review(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, _ = Review.objects.update_or_create(
                user=request.user,
                calculator=calculator,
                defaults={
                    "rating": form.cleaned_data["rating"],
                    "title": form.cleaned_data["title"],
                    "comment": form.cleaned_data["comment"],
                    "is_approved": False,
                },
            )
            messages.success(request, f"Review submitted for moderation: {review.title}")
        else:
            messages.error(request, "Review is invalid.")
    return redirect("calculator_detail", slug=slug)


def compare_calculators(request):
    slugs = request.GET.getlist("compare")
    calculators = CalculatorPost.objects.filter(slug__in=slugs)[:3]
    all_calculators = CalculatorPost.objects.order_by("title")
    context = {
        "calculators": calculators,
        "all_calculators": all_calculators,
        "seo_title": "Compare Calculators",
        "seo_description": "Side-by-side calculator comparison.",
    }
    return render(request, "compare.html", context)


@login_required
def save_comparison(request):
    if request.method == "POST":
        slugs = request.POST.getlist("compare")
        name = request.POST.get("name", "My comparison").strip() or "My comparison"
        calculators = list(CalculatorPost.objects.filter(slug__in=slugs)[:3])
        if len(calculators) >= 2:
            comparison = SavedComparison.objects.create(user=request.user, name=name)
            comparison.calculators.set(calculators)
            messages.success(request, "Comparison saved.")
        else:
            messages.error(request, "Choose at least two calculators.")
    return redirect("compare_calculators")


def buy_now_redirect(request, slug):
    calculator = get_object_or_404(CalculatorPost, slug=slug)
    AffiliateClick.objects.create(
        calculator=calculator,
        user=request.user if request.user.is_authenticated else None,
        source=request.GET.get("source", "direct"),
        page=request.GET.get("page", "catalog"),
    )
    CalculatorPost.objects.filter(pk=calculator.pk).update(click_count=F("click_count") + 1)
    return redirect(calculator.buy_url)


def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(
        request,
        "articles.html",
        {
            "articles": articles,
            "seo_title": "Buying Guides and Calculator Articles",
            "seo_description": "Read calculator buying guides and exam-focused recommendations.",
        },
    )


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(
        request,
        "article_detail.html",
        {
            "article": article,
            "seo_title": article.seo_title or article.title,
            "seo_description": article.seo_description or article.summary[:150],
            "og_image": article.og_image_url,
        },
    )


def recommender_quiz(request):
    recommendation = None
    if request.method == "POST":
        use_case = request.POST.get("use_case")
        budget = request.POST.get("budget")
        graphing = request.POST.get("graphing") == "yes"

        calculators = CalculatorPost.objects.all()
        if budget == "low":
            calculators = calculators.filter(price__lte=50)
        elif budget == "mid":
            calculators = calculators.filter(price__lte=120)

        if graphing:
            calculators = calculators.filter(category="graphing")
        elif use_case in {"exam", "student"}:
            calculators = calculators.filter(category__in=["scientific", "basic"])
        elif use_case == "finance":
            calculators = calculators.filter(category="financial")

        recommendation = calculators.order_by("-rating", "price").first()

    return render(
        request,
        "quiz.html",
        {
            "recommendation": recommendation,
            "seo_title": "Calculator Recommender Quiz",
            "seo_description": "Find the best calculator for your budget and use case.",
        },
    )


def ai_assistant(request):
    answer = None
    if request.method == "POST":
        question = request.POST.get("question", "").lower()
        budget = request.POST.get("budget", "").strip()

        query = CalculatorPost.objects.all()
        if budget:
            try:
                query = query.filter(price__lte=Decimal(budget))
            except Exception:
                pass

        if "engineer" in question or "graph" in question:
            suggestion = query.filter(category="graphing").order_by("-rating", "price").first()
        elif "finance" in question or "business" in question:
            suggestion = query.filter(category="financial").order_by("-rating", "price").first()
        else:
            suggestion = query.order_by("-rating", "price").first()

        if suggestion:
            answer = f"Recommended: {suggestion.title} ({suggestion.brand}) at ${suggestion.price}."
        else:
            answer = "No matching calculator found yet."

    return render(
        request,
        "assistant.html",
        {
            "answer": answer,
            "seo_title": "Calculator AI Assistant",
            "seo_description": "Get calculator recommendations by question and budget.",
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form, "seo_title": "Register"})


def robots_txt(_request):
    lines = [
        "User-Agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Sitemap: /sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
