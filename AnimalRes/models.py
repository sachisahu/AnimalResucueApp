from django.db import models


# Create your models here.
class Rescuers(models.Model):
    userName = models.CharField(max_length=100)
    loginCode = models.CharField(max_length=100, unique=True)


class Animal(models.Model):
    animal = models.CharField(max_length=100, null=True)
    pic_url = models.CharField(max_length=1000,null=True)


class AnimalRescued(models.Model):
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    pickup_latitude = models.CharField(max_length=100, null=True)
    pickup_longitude = models.CharField(max_length=100, null=True)
    pickup_landmark = models.CharField(max_length=100, null=True)
    pickup_animalPhoto = models.CharField(max_length=1000, null=True)
    animal = models.CharField(max_length=100, null=True)
    pickup_status = models.CharField(max_length=100)
    release_date = models.DateField(null=True)
    release_time = models.TimeField(null=True)
    release_latitude = models.CharField(max_length=100, null=True)
    release_longitude = models.CharField(max_length=100, null=True)
    release_landmark = models.CharField(max_length=100, null=True)
    release_animalPhoto = models.CharField(max_length=1000, null=True)
    release_status = models.CharField(max_length=100, null=True)
    distance_variance = models.CharField(max_length=100, null=True)
