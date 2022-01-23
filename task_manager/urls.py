from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("add-task/", views.add_task),
    path("tasks/", views.display_tasks),
    path("delete-task/<int:index>/", views.delete_task),
    path("delete-task/<int:index>/<str:route>/", views.delete_task),
    path("complete_task/<int:index>/", views.mark_complete),
    path("complete_task/<int:index>/<str:route>/", views.mark_complete),
    path("completed_tasks/", views.display_completed_tasks),
    path("all_tasks/", views.display_all_tasks),
]
