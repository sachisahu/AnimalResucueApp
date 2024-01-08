from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages




def userLogin(request):
    if request.method == 'POST':
        if 'loginBtn' in request.POST:
            userID = request.POST.get('userId')
            userPass = request.POST.get('userpassword')
            user = authenticate(request, username=userID, password=userPass)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                messages.info(request,'Invalid Credentials')
                return render(request, "login.html")




    return render(request, "login.html")

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
        return HttpResponse('Unable to Perform the operation.')
