from django.contrib import admin
from django.urls import path
from tasks import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("add-task/", views.add_task),
    path("tasks/", views.display_tasks),
    path("delete-task/<int:index>/", views.delete_task)
    # Add all your views here
]
