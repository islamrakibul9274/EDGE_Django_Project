from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import AffiliateClick, CalculatorPost, PriceAlert


class CalculatorPostModelTests(TestCase):
    def test_generates_slug_and_badges(self):
        calc = CalculatorPost.objects.create(
            title="TI-84 Plus",
            description="Graphing calculator",
            image="https://example.com/calc.png",
            buy_url="https://example.com/buy",
            price=Decimal("100.00"),
            original_price=Decimal("120.00"),
            category="graphing",
            brand="Texas Instruments",
            rating=Decimal("4.80"),
            click_count=20,
            is_featured=True,
        )
        self.assertTrue(calc.slug)
        self.assertIn("Top Rated", calc.promotional_badges)

    def test_rejects_invalid_price(self):
        calc = CalculatorPost(
            title="Bad Price",
            description="Bad",
            buy_url="https://example.com/buy",
            price=Decimal("0.00"),
            category="scientific",
            brand="Any",
        )
        with self.assertRaises(ValidationError):
            calc.full_clean()


class CatalogViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@example.com", "password123")
        self.calc = CalculatorPost.objects.create(
            title="Casio FX-991EX",
            description="Great scientific calculator",
            image="https://example.com/casio.png",
            buy_url="https://example.com/casio-buy",
            price=Decimal("35.00"),
            category="scientific",
            brand="Casio",
            rating=Decimal("4.60"),
            is_featured=True,
            specifications={"Display": "Natural-VPAM"},
        )

    def test_catalog_search(self):
        response = self.client.get(reverse("calculator_list"), {"q": "casio"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Casio FX-991EX")

    def test_buy_redirect_tracks_click(self):
        response = self.client.get(reverse("buy_now_redirect", args=[self.calc.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AffiliateClick.objects.count(), 1)
        self.calc.refresh_from_db()
        self.assertEqual(self.calc.click_count, 1)

    def test_price_alert_requires_login(self):
        response = self.client.post(reverse("add_price_alert", args=[self.calc.slug]), {"target_price": "20.00"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_price_alert_creation(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("add_price_alert", args=[self.calc.slug]), {"target_price": "20.00"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PriceAlert.objects.filter(user=self.user, calculator=self.calc).exists())

    def test_robots_txt(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sitemap", response.content.decode())
