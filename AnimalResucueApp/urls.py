from django.contrib import admin
from django.urls import path,include
from AnimalResucueApp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('AnimalRes.urls')),
    path('login',views.userLogin),
    path('logout',views.logOutUser),
]
