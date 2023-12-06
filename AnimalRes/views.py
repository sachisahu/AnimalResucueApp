from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse


def home(request):
    return render(request, "home.html")


@login_required(login_url='/login')
def registerAnimal(request):
    return render(request, "NewAnimal.html")
