import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse
from AnimalRes.models import Animal,AnimalRescued
from AnimalRes.utils import uploadResourcesToDigitalOcean


def home(request):
    return render(request, "home.html")


@login_required(login_url='/login')
def registerAnimal(request):
    animals = Animal.objects.all()
    context ={
        "animals":animals,
    }
    if request.method == 'POST':
        if 'saveButton' in request.POST:
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            landmark = request.POST.get('landmark')
            image = request.FILES['fileInputImage']
            animal = request.POST.get('animalType')
            status = request.POST.get('status')

            print(image)

            picURLurl = uploadResourcesToDigitalOcean('picupAnimal',image)
            print(picURLurl)

            animalRes = AnimalRescued(
                pickup_date=datetime.datetime.today(),
                pickup_time=datetime.datetime.now(),
                pickup_latitude = latitude,
                pickup_longitude= longitude,
                pickup_landmark=landmark,
                pickup_animalPhoto = picURLurl,
                animal = Animal.objects.get(id = animal),
                pickup_status = status
            )
            animalRes.save()



    return render(request, "NewAnimal.html",context)
