import os
from datetime import timedelta

from django.conf import settings

from celery import Celery
from celery.decorators import periodic_task

# set DJANGO_SETTINGS_MODULE with value task_manager.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings")

# The first argument to Celery is the name of the current module.
# This is only needed so that names can be automatically generated
# when the tasks are defined in the __main__ module.
app = Celery("task_manager")
app.config_from_object("django.conf:settings")
# discovers new task from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
