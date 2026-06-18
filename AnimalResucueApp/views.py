from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from  AnimalResucueApp import settings




def userLogin(request):
    context = {
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }
    if request.method == 'POST':
        userID = request.POST.get('userId')
        userPass = request.POST.get('userpassword')
        user = authenticate(request, username=userID, password=userPass)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'The user ID or password you entered is incorrect.')
            return render(request, "login.html",context)

    return render(request, "login.html",context)

def userSignUP(request):

    if request.method == 'POST':
        if 'loginBtn' in request.POST:
            print("Hitting")
            userID = request.POST.get('userId')
            userPass = request.POST.get('userpassword')
            user = User.objects.create_user(userID, userID, userPass)

    return render(request, "login.html")

def logOutUser(request):
    if request.user is not None:
        logout(request)
        return redirect('/login')
    else:
        return HttpResponse('The logout request could not be completed.')
