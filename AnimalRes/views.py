import datetime
import json
import time
from  AnimalResucueApp import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from AnimalRes.models import Animal, AnimalRescued, Rescuers
from AnimalRes.utils import uploadResourcesToDigitalOcean,moveImages
from django.contrib.auth.models import User
from django.contrib import messages



def home(request):
    context = {
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }
    return render(request, "home.html",context)


@login_required(login_url='/login')
def registerAnimal(request):
    animals = Animal.objects.all()
    context = {
        "animals": animals,
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }
    if request.method == 'POST':
        if 'saveButton' in request.POST:
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            landmark = request.POST.get('landmark')
            image = request.FILES['fileInputImage']
            animal = request.POST.get('animalType')
            status = request.POST.get('status')
            otherInput = request.POST.get('otherInput')

            if animal == 'others':
                animal = otherInput

            picURLurl = uploadResourcesToDigitalOcean('picupAnimal', image)


            animalRes = AnimalRescued(
                pickup_date=datetime.datetime.today(),
                pickup_time=datetime.datetime.now(),
                pickup_latitude=latitude,
                pickup_longitude=longitude,
                pickup_landmark=landmark,
                pickup_animalPhoto=picURLurl,
                animal=animal,
                pickup_status=status
            )
            animalRes.save()
            return redirect("/registerAnimal")

    return render(request, "RegisterAnimal.html", context)


@login_required(login_url='/login')
def releaseAnimal(request):
    context = {
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }
    if request.method == 'POST':
        if 'saveButton' in request.POST:
            slno = request.POST.get('release_slno')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            landmark = request.POST.get('landmark')
            image = request.FILES['fileInputImage']
            status = request.POST.get('status')
            variance = request.POST.get('variance')

            picURLurl = uploadResourcesToDigitalOcean('releaseAnimal', image)

            updateRelaesedAnimal = AnimalRescued.objects.get(id=slno)
            updateRelaesedAnimal.release_date = datetime.datetime.today()
            updateRelaesedAnimal.release_time = datetime.datetime.now()
            updateRelaesedAnimal.release_latitude = latitude
            updateRelaesedAnimal.release_longitude = longitude
            updateRelaesedAnimal.release_landmark = landmark
            updateRelaesedAnimal.release_status = status
            updateRelaesedAnimal.release_animalPhoto = picURLurl
            updateRelaesedAnimal.distance_variance = variance
            updateRelaesedAnimal.save()

            return redirect('/releaseAnimal')

        if 'getAnimalDetails' in request.POST:
            slno = request.POST.get('reqslno')
            animalDetails = AnimalRescued.objects.all().filter(id=slno).first()
            if animalDetails:
                if animalDetails.release_status is None:
                    animalData = {
                        'id': animalDetails.id,
                        'type': animalDetails.animal,
                        'photo_url': animalDetails.pickup_animalPhoto,
                        'landmark': animalDetails.pickup_landmark,
                        'longitude': animalDetails.pickup_longitude,
                        'latitude': animalDetails.pickup_latitude,
                    }
                    return JsonResponse({'message': json.dumps(animalData), 'status': 200})
                else:
                    return JsonResponse({'message': "Animal Already Released", 'status': 404})

            else:
                return JsonResponse({'message': "No Animal Found", 'status': 404})

    return render(request, "ReleaseAnimal.html",context)


@login_required(login_url='/login')
def report(request):
    # allResecues = AnimalRescued.objects.all().order_by('-pickup_date', '-release_date')
    allResecues = AnimalRescued.objects.all().order_by('-id')
    context = {
        "allResecues": allResecues,
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }

    if request.method == 'POST':
        if 'removeARecordButton' in request.POST:
            slno = request.POST.get("recordID")

            removeObj = AnimalRescued.objects.all().filter(id = slno).first()
            removeObj.delete()
            return redirect("/report")

    return render(request, 'report.html', context)

@login_required(login_url='/login')
def admin(request):
    if not request.user.is_superuser:
        return HttpResponse("Page Not Found 404")

    rescuers = Rescuers.objects.all()

    context = {
        "users": rescuers,
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }

    if request.method == 'POST':
        if 'uplodeAnimalPictureToListBtn' in request.POST:
            animalName = request.POST.get("AnimalNameUplode")
            animalPicture = request.FILES['AnimalPictureUplode']

            animalPictureUrl = uploadResourcesToDigitalOcean("animalPics", animalPicture)

            newAnimal = Animal(
                animal=animalName,
                pic_url=animalPictureUrl
            )
            newAnimal.save()
            context["haveMessage"] = True,
            context["mess"] = "Animal Added Successfully"
            messages.info(request, 'Animal Added Successfully')
            return render(request, 'Admin.html', context)

        if 'saveCreateUserBtn' in request.POST:
            userName = request.POST.get("UserNameCreateUser")
            password = request.POST.get('PasswordCreateUser')

            checkUserExistes = Rescuers.objects.all().filter(userName=userName).first()

            if checkUserExistes:
                messages.info(request, 'Username Already Existes')
                return render(request, 'Admin.html', context)
            else:
                User.objects.create_user(userName, userName, password)
                rescuers = Rescuers(
                    userName=userName
                )
                rescuers.save()
                messages.info(request, 'Username Created Successfully')
                return render(request, 'Admin.html', context)

        if 'updateUserPasswordBtn' in request.POST:
            userName = request.POST.get("updatePasswordUsername")
            password = request.POST.get('updatePasswordPassword')

            checkUserExistes = User.objects.all().filter(username=userName).first()
            if checkUserExistes:
                u = User.objects.get(username__exact=userName)
                u.set_password(password)
                u.save()

                messages.info(request, 'Password Updated Successfully')
                return render(request, 'Admin.html', context)

    return render(request, "Admin.html", context)


def reuplodeSpaceChanges(request,start,end):
    start = int(start)
    end = int(end)

    for cid in range(start,end):
        currentObj = AnimalRescued.objects.all().filter(id = cid).first()
        if currentObj is not None:
            newurlpicup = moveImages(currentObj.pickup_animalPhoto,"picupAnimal")
            print(f"PicUploded Pickup id: {cid}")
            currentObj.pickup_animalPhoto = newurlpicup
            currentObj.save()
            print(f"Updated On Pickup DB id: {cid}")

            if currentObj.release_animalPhoto is not None:
                newurlrelease = moveImages(currentObj.release_animalPhoto,"releaseAnimal")
                print(f"PicUploded release id: {cid}")
                currentObj.release_animalPhoto = newurlrelease
                currentObj.save()
                print(f"Updated On release DB id: {cid}")
            else:
                print(f"Animal Not Yet released  for id:{cid}")

        else:
            print(f"Row for id:{cid} Not found")


    return HttpResponse("Completed")

def reuplodeSpaceChanges2(request,start,end):
    start = int(start)
    end = int(end)

    for cid in range(start,end):
        currentObj = Animal.objects.all().filter(id = cid).first()
        if currentObj is not None:
            newurlpicup = moveImages(currentObj.pic_url,"animalPics")
            print(f"PicUploded Pickup id: {cid}")
            currentObj.pic_url = newurlpicup
            currentObj.save()
            print(f"Updated On Pickup DB id: {cid}")

        else:
            print(f"Row for id:{cid} Not found")


    return HttpResponse("Completed")


