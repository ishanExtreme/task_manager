from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

tasks = []


def add_task(request):
    """
    Add a new task to the list
    """
    task_value = request.GET.get("task")
    tasks.append(task_value)
    return HttpResponseRedirect("/tasks")


def display_tasks(request):
    """
    Display All tasks
    """
    return render(request, "tasks.html", {"tasks": tasks})


def delete_task(request, index):
    """
    Delete task from the list. Takes index of the task as parameter
    """
    tasks.pop(index - 1)
    return HttpResponseRedirect("/tasks")
