from django.urls import path
from AnimalRes import views

urlpatterns = [
    path('', views.home),

]
