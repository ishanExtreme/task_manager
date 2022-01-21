from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

tasks = []
complete = []


def add_task(request):
    """
    Add a new task to the list
    """
    task_value = request.GET.get("task")
    tasks.append(task_value)
    return HttpResponseRedirect("/tasks")


def display_tasks(request):
    """
    Display incomplete tasks
    """
    return render(request, "tasks.html", {"tasks": tasks})


def delete_task(request, index):
    """
    Delete task from the list. Takes index of the task as parameter
    """
    tasks.pop(index - 1)
    return HttpResponseRedirect("/tasks")


def mark_complete(request, index):
    """
    Marks task as complete by removing it from taks list and
    adding it to complete list. Takes index of the task as parameter
    """
    index -= 1
    complete.append(tasks.pop(index))
    return HttpResponseRedirect("/tasks")


def display_completed_tasks(request):
    """
    Displays completed tasks
    """
    return render(request, "completed.html", {"tasks": complete})


def display_all_tasks(request):
    """
    Displays both pending and completed tasks
    """
    return render(request, "all_task.html", {"complete": complete, "pending": tasks})
