from django.contrib import admin
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
    # Add all your views here
]
