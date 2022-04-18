"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks.views import (
    UserCreationView,
    UserLoginView,
    LogoutView,
    TaskListView,
    TaskDeleteView,
    AddTaskView,
    UpdateTaskView,
    home_view,
    handle_schedule_request,
    UpdateScheduleView,
)
from rest_framework.authtoken import views
from tasks.apiviews import (
    TaskViewSet,
    StageListView,
    UserCreation,
    UserGet,
    StageViewset,
    BoardViewSet,
)

from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router = SimpleRouter()
# User api
router.register("api/user/register", UserCreation)
router.register("api/user/me", UserGet)
router.register("api/board", BoardViewSet)
router.register("api/stage", StageListView)

# Task api
# router.register("api/task", TaskViewSet)
# router.register("api/history", HistroryViewSet)

# nested routes
# history route
# history = routers.NestedSimpleRouter(router, "api/task", lookup="task")
# history.register("history", HistroryViewSet)
# Stage route
stage = routers.NestedSimpleRouter(router, "api/board", lookup="board")
stage.register("stage", StageViewset)
# Task route
task = routers.NestedSimpleRouter(router, "api/stage", lookup="stage")
task.register("task", TaskViewSet)

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("", home_view),
        path("user/signup/", UserCreationView.as_view()),
        path("user/login/", UserLoginView.as_view()),
        path("user/logout/", LogoutView.as_view()),
        path("tasks/", TaskListView.as_view()),
        path("delete-task/<pk>/", TaskDeleteView.as_view()),
        path("update-task/<pk>/", UpdateTaskView.as_view()),
        path("create-task/", AddTaskView.as_view()),
        path("update-schedule/<pk>/", UpdateScheduleView.as_view()),
        path("report/", handle_schedule_request),
        path("api/token", views.obtain_auth_token),
    ]
    + router.urls
    + stage.urls
    + task.urls
)
