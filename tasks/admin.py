from django.contrib import admin

# Register your models here.

from tasks.models import Task, History, Schedule, Board, Stage

admin.sites.site.register(Task)
admin.sites.site.register(History)
admin.sites.site.register(Schedule)
admin.sites.site.register(Board)
admin.sites.site.register(Stage)
