from django.contrib import admin
from AnimalRes.models import Animal, AnimalRescued, Rescuers, RescueLocation

# Register your models here.
admin.site.register(RescueLocation)
admin.site.register(Rescuers)
admin.site.register(Animal)
admin.site.register(AnimalRescued)
