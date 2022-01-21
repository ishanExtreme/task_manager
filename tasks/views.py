from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

tasks = []


def add_task(request):
    task_value = request.GET.get("task")
    tasks.append(task_value)
    return HttpResponseRedirect("/tasks")


def display_tasks(request):
    return render(request, "tasks.html", {"tasks": tasks})


def delete_task(request, index):
    tasks.pop(index - 1)
    return HttpResponseRedirect("/tasks")
