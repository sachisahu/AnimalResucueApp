import datetime
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from AnimalRes.models import Animal, AnimalRescued
from AnimalRes.utils import uploadResourcesToDigitalOcean


def home(request):
    return render(request, "home.html")


@login_required(login_url='/login')
def registerAnimal(request):
    animals = Animal.objects.all()
    context = {
        "animals": animals,
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


            print(image)

            picURLurl = uploadResourcesToDigitalOcean('picupAnimal', image)
            print(picURLurl)

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

    return render(request, "NewAnimal.html", context)


@login_required(login_url='/login')
def releaseAnimal(request):
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
                    print("hittingrelese" + str(animalDetails))
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
                return JsonResponse({'message': "Invalid Slno", 'status': 404})

    return render(request, "ReleaseAnimal.html")


@login_required(login_url='/login')
def report(request):
    allResecues = AnimalRescued.objects.all()
    context = {
        "allResecues":allResecues

    }
    return render(request, 'report.html',context)
