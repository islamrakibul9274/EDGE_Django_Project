from django.contrib import admin
from django.urls import path
from blog.views import home, calculator_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Home Page URL
    path('blog/', calculator_list, name='calculator_list'),  # Blog Page URL
]
