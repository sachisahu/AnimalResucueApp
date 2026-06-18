import datetime
import json
import time
import csv
from  AnimalResucueApp import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from AnimalRes.models import Animal, AnimalRescued, Rescuers, RescueLocation
from AnimalRes.utils import uploadResourcesToDigitalOcean, uploadResourcesToCloudflareR2, moveImages, generate_demo_ai_review
from django.contrib.auth.models import User
from django.contrib import messages


DEMO_PLACEHOLDER_IMAGE = ""
ACCESS_DENIED_MESSAGE = "You do not have permission to access this page."


def get_rescuer_profile(user):
    if not user or not user.is_authenticated:
        return None
    return Rescuers.objects.filter(userName=user.username).select_related("location").first()


def get_user_location(user):
    rescuer = get_rescuer_profile(user)
    return rescuer.location if rescuer else None


def is_location_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    rescuer = get_rescuer_profile(user)
    return bool(rescuer and rescuer.user_type == "location_admin")


def can_view_operations(user):
    return user.is_superuser or is_location_admin(user)


def scoped_rescues_for_user(user):
    rescues = AnimalRescued.objects.select_related("location").all()
    if user.is_superuser:
        return rescues
    user_location = get_user_location(user)
    if user_location:
        return rescues.filter(location=user_location)
    return rescues.none()



def home(request):
    location = get_user_location(request.user)
    rescuer = get_rescuer_profile(request.user)
    total_rescues = AnimalRescued.objects.count() if request.user.is_superuser else scoped_rescues_for_user(request.user).count() if request.user.is_authenticated else 0
    open_cases = scoped_rescues_for_user(request.user).filter(release_status__isnull=True).count() if request.user.is_authenticated else 0
    context = {
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl,
        "location": location,
        "rescuer": rescuer,
        "is_location_admin": is_location_admin(request.user),
        "can_view_operations": can_view_operations(request.user),
        "total_rescues": total_rescues,
        "open_cases": open_cases,
    }
    return render(request, "home.html",context)


@login_required(login_url='/login')
def registerAnimal(request):
    animals = Animal.objects.all()
    user_location = get_user_location(request.user)
    locations = RescueLocation.objects.filter(is_active=True).order_by("name")
    context = {
        "animals": animals,
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl,
        "location": user_location,
        "locations": locations,
        "can_view_operations": can_view_operations(request.user),
    }
    if request.method == 'POST':
        if 'saveButton' in request.POST:
            latitude = request.POST.get('latitude') or ""
            longitude = request.POST.get('longitude') or ""
            landmark = request.POST.get('landmark')
            image = request.FILES.get('fileInputImage')
            animal = request.POST.get('animalType')
            status = request.POST.get('status')
            otherInput = request.POST.get('otherInput')

            if animal == 'others':
                animal = otherInput

            try:
                picURLurl = uploadResourcesToCloudflareR2('pickupAnimal', image) if image else DEMO_PLACEHOLDER_IMAGE
            except Exception as exc:
                messages.info(request, f"Image upload failed: {exc}")
                return redirect("/registerAnimal")
            selected_location = user_location
            if request.user.is_superuser:
                selected_location = RescueLocation.objects.filter(id=request.POST.get("location")).first() or user_location

            animalRes = AnimalRescued(
                location=selected_location,
                pickup_date=datetime.datetime.today(),
                pickup_time=datetime.datetime.now(),
                pickup_latitude=latitude,
                pickup_longitude=longitude,
                pickup_landmark=landmark,
                pickup_animalPhoto=picURLurl,
                animal=animal,
                pickup_status=status,
            )
            animalRes.save()
            messages.success(request, 'Rescue case saved successfully.')
            return redirect("/registerAnimal")

    return render(request, "RegisterAnimal.html", context)


@login_required(login_url='/login')
def releaseAnimal(request):
    if not can_view_operations(request.user):
        return HttpResponse(ACCESS_DENIED_MESSAGE)

    user_location = get_user_location(request.user)
    context = {
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl,
        "location": user_location,
        "can_view_operations": can_view_operations(request.user),
    }
    if request.method == 'POST':
        if 'saveButton' in request.POST:
            slno = request.POST.get('release_slno')
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            landmark = request.POST.get('landmark')
            image = request.FILES.get('fileInputImage')
            status = request.POST.get('status')
            variance = request.POST.get('variance') or ""

            try:
                picURLurl = uploadResourcesToCloudflareR2('releaseAnimal', image) if image else DEMO_PLACEHOLDER_IMAGE
            except Exception as exc:
                messages.info(request, f"Image upload failed: {exc}")
                return redirect('/releaseAnimal')

            updateRelaesedAnimal = scoped_rescues_for_user(request.user).filter(id=slno).first()
            if updateRelaesedAnimal is None:
                messages.info(request, "No matching rescue record was found for your assigned location.")
                return redirect('/releaseAnimal')
            updateRelaesedAnimal.release_date = datetime.datetime.today()
            updateRelaesedAnimal.release_time = datetime.datetime.now()
            updateRelaesedAnimal.release_latitude = latitude
            updateRelaesedAnimal.release_longitude = longitude
            updateRelaesedAnimal.release_landmark = landmark
            updateRelaesedAnimal.release_status = status
            updateRelaesedAnimal.release_animalPhoto = picURLurl
            updateRelaesedAnimal.distance_variance = variance
            updateRelaesedAnimal.save()
            messages.success(request, 'Release record saved successfully.')

            return redirect('/releaseAnimal')

        if 'getAnimalDetails' in request.POST:
            slno = request.POST.get('reqslno')
            animalDetails = scoped_rescues_for_user(request.user).filter(id=slno).first()
            if animalDetails:
                if animalDetails.release_status is None:
                    animalData = {
                        'id': animalDetails.id,
                        'type': animalDetails.animal,
                        'photo_url': animalDetails.pickup_animalPhoto,
                        'landmark': animalDetails.pickup_landmark,
                        'longitude': animalDetails.pickup_longitude,
                        'latitude': animalDetails.pickup_latitude,
                        'location': animalDetails.location.name if animalDetails.location else "Unassigned",
                    }
                    return JsonResponse({'message': json.dumps(animalData), 'status': 200})
                else:
                    return JsonResponse({'message': "This rescue case has already been released.", 'status': 404})

            else:
                return JsonResponse({'message': "No rescue case was found for the entered case number.", 'status': 404})

    return render(request, "ReleaseAnimal.html",context)


@login_required(login_url='/login')
def report(request):
    if not can_view_operations(request.user):
        return HttpResponse(ACCESS_DENIED_MESSAGE)

    # allResecues = AnimalRescued.objects.all().order_by('-pickup_date', '-release_date')
    selected_location_id = request.GET.get("location")
    selected_status = request.GET.get("status")
    allResecues = scoped_rescues_for_user(request.user).order_by('-id')
    if request.user.is_superuser and selected_location_id:
        allResecues = allResecues.filter(location_id=selected_location_id)
    if selected_status == "open":
        allResecues = allResecues.filter(release_status__isnull=True)
    elif selected_status == "released":
        allResecues = allResecues.filter(release_status__isnull=False)
    locations = RescueLocation.objects.filter(is_active=True).order_by("name")

    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="animal_rescue_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "Case ID",
            "Location",
            "Animal",
            "Pickup Date",
            "Pickup Landmark",
            "Pickup Status",
            "Release Date",
            "Release Landmark",
            "Release Status",
            "Distance Variance",
            "AI Risk",
            "AI Review",
        ])
        for rescue in allResecues:
            writer.writerow([
                rescue.id,
                rescue.location.name if rescue.location else "Unassigned",
                rescue.animal,
                rescue.pickup_date,
                rescue.pickup_landmark,
                rescue.pickup_status,
                rescue.release_date or "",
                rescue.release_landmark or "",
                rescue.release_status or "Release pending",
                rescue.distance_variance or "",
                rescue.ai_risk_level or "",
                rescue.ai_release_review or rescue.ai_pickup_review or "",
            ])
        return response

    context = {
        "allResecues": allResecues,
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl,
        "locations": locations,
        "selected_location_id": selected_location_id,
        "selected_status": selected_status,
        "location": get_user_location(request.user),
        "can_view_operations": can_view_operations(request.user),
        "total_count": allResecues.count(),
        "open_count": allResecues.filter(release_status__isnull=True).count(),
        "released_count": allResecues.filter(release_status__isnull=False).count(),
    }

    if request.method == 'POST':
        if 'removeARecordButton' in request.POST:
            if not request.user.is_superuser:
                return HttpResponse(ACCESS_DENIED_MESSAGE)
            slno = request.POST.get("recordID")

            removeObj = AnimalRescued.objects.all().filter(id=slno).first()
            if removeObj:
                removeObj.delete()
            return redirect("/report")

        if 'generateAiReviewButton' in request.POST:
            slno = request.POST.get("recordID")
            rescue = scoped_rescues_for_user(request.user).filter(id=slno).first()
            if rescue is None:
                messages.info(request, "No rescue record was found for AI review.")
                return redirect("/report")

            pickup_review, pickup_risk = generate_demo_ai_review(
                rescue.animal,
                rescue.pickup_status,
                rescue.pickup_landmark,
                "pickup",
            )
            rescue.ai_pickup_review = pickup_review
            rescue.ai_risk_level = pickup_risk

            if rescue.release_status:
                release_review, release_risk = generate_demo_ai_review(
                    rescue.animal,
                    rescue.release_status,
                    rescue.release_landmark,
                    "release",
                )
                rescue.ai_release_review = release_review
                rescue.ai_risk_level = release_risk

            rescue.save()
            messages.success(request, f"AI review generated successfully for case #{rescue.id}.")
            redirect_url = "/report"
            selected_location_id = request.GET.get("location")
            if selected_location_id:
                redirect_url = f"/report?location={selected_location_id}"
            return redirect(redirect_url)

    return render(request, 'report.html', context)

@login_required(login_url='/login')
def admin(request):
    if not can_view_operations(request.user):
        return HttpResponse(ACCESS_DENIED_MESSAGE)

    user_location = get_user_location(request.user)
    if request.user.is_superuser:
        rescuers = Rescuers.objects.select_related("location").all()
        locations = RescueLocation.objects.all().order_by("name")
    else:
        rescuers = Rescuers.objects.select_related("location").filter(location=user_location)
        locations = RescueLocation.objects.filter(id=user_location.id) if user_location else RescueLocation.objects.none()

    context = {
        "users": rescuers,
        "locations": locations,
        "location": user_location,
        "is_location_admin": is_location_admin(request.user),
        "can_view_operations": can_view_operations(request.user),
        "logourl":settings.logoUrl,
        "logofavicon":settings.logoFaviconUrl
    }

    if request.method == 'POST':
        if 'uplodeAnimalPictureToListBtn' in request.POST:
            if not request.user.is_superuser:
                return HttpResponse(ACCESS_DENIED_MESSAGE)
            animalName = (request.POST.get("AnimalNameUplode") or "").strip()
            animalPicture = request.FILES.get('AnimalPictureUplode')

            if Animal.objects.filter(animal__iexact=animalName).exists():
                messages.info(request, 'This animal category already exists.')
                return redirect('/admin')

            try:
                animalPictureUrl = uploadResourcesToCloudflareR2("animalPics", animalPicture) if animalPicture else DEMO_PLACEHOLDER_IMAGE
                print("animalPictureUrl",animalPictureUrl)
            except Exception as exc:
                messages.info(request, f"Image upload failed: {exc}")
                return redirect('/admin')

            newAnimal = Animal(
                animal=animalName,
                pic_url=animalPictureUrl
            )
            newAnimal.save()
            context["haveMessage"] = True,
            context["mess"] = "Animal category saved successfully."
            messages.info(request, 'Animal category saved successfully.')
            return render(request, 'Admin.html', context)

        if 'saveCreateUserBtn' in request.POST:
            userName = request.POST.get("UserNameCreateUser")
            password = request.POST.get('PasswordCreateUser')
            requested_user_type = request.POST.get("UserTypeCreateUser") or "normal"

            if request.user.is_superuser:
                location = RescueLocation.objects.filter(id=request.POST.get("UserLocationCreateUser")).first()
                user_type = requested_user_type if requested_user_type in ["normal", "location_admin"] else "normal"
            else:
                location = user_location
                user_type = "normal"

            checkUserExistes = Rescuers.objects.all().filter(userName=userName).first()

            if checkUserExistes:
                messages.info(request, 'A user account with this user name already exists.')
                return render(request, 'Admin.html', context)
            else:
                User.objects.create_user(userName, userName, password)
                rescuers = Rescuers(
                    userName=userName,
                    user_type=user_type,
                    location=location,
                )
                rescuers.save()
                messages.info(request, 'User account created successfully.')
                return render(request, 'Admin.html', context)

        if 'saveCreateLocationBtn' in request.POST:
            if not request.user.is_superuser:
                return HttpResponse(ACCESS_DENIED_MESSAGE)
            locationName = request.POST.get("LocationName")
            locationCity = request.POST.get("LocationCity")
            if locationName:
                RescueLocation.objects.get_or_create(
                    name=locationName,
                    defaults={"city": locationCity or locationName},
                )
                messages.info(request, 'Rescue location created successfully.')
            return redirect('/admin')

        if 'assignUserLocationBtn' in request.POST:
            if not request.user.is_superuser:
                return HttpResponse(ACCESS_DENIED_MESSAGE)
            userName = request.POST.get("assignLocationUsername")
            location = RescueLocation.objects.filter(id=request.POST.get("assignLocation")).first()
            rescuer = Rescuers.objects.filter(userName=userName).first()
            if rescuer and location:
                rescuer.location = location
                rescuer.save()
                messages.info(request, 'Location access assigned successfully.')
            return redirect('/admin')

        if 'updateUserPasswordBtn' in request.POST:
            userName = request.POST.get("updatePasswordUsername")
            password = request.POST.get('updatePasswordPassword')

            checkUserExistes = User.objects.all().filter(username=userName).first()
            if not request.user.is_superuser:
                allowed_rescuer = Rescuers.objects.filter(
                    userName=userName,
                    location=user_location,
                    user_type="normal",
                ).first()
                if allowed_rescuer is None:
                    return HttpResponse(ACCESS_DENIED_MESSAGE)

            if checkUserExistes:
                u = User.objects.get(username__exact=userName)
                u.set_password(password)
                u.save()

                messages.info(request, 'User password updated successfully.')
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


