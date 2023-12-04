from django.shortcuts import render, HttpResponse


def home(request):
    return render(request, "home.html")


def registerAnimal(request):
    return render(request, "NewAnimal.html")
