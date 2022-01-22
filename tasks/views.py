from turtle import title
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from tasks.models import Task

# tasks = []
# complete = []


def add_task(request):
    """
    Add a new task to the list
    """
    task_value = request.GET.get("task")
    Task(title=task_value).save()
    return HttpResponseRedirect("/tasks")


def display_tasks(request):
    """
    Display incomplete tasks
    """
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False)
    if search_term:
        tasks = tasks.filter(title__icontains=search_term)

    return render(request, "tasks.html", {"tasks": tasks})


def delete_task(request, index):
    """
    Delete task from the list. Takes index of the task as parameter
    """
    Task.objects.filter(id=index).update(deleted=True)
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
