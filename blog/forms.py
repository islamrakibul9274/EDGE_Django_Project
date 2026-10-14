from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import BackInStockSubscription, NewsletterSubscription, PriceAlert, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "title", "comment")


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ("email",)


class BackInStockForm(forms.ModelForm):
    class Meta:
        model = BackInStockSubscription
        fields = ("email",)


class PriceAlertForm(forms.ModelForm):
    class Meta:
        model = PriceAlert
        fields = ("target_price",)
