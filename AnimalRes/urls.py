from django.urls import path
from AnimalRes import views

urlpatterns = [
    path('', views.home),
    path('registerAnimal', views.registerAnimal),
    path('releaseAnimal', views.releaseAnimal),
    path('report', views.report),
    path('admin', views.admin),
    path('reuplodeSpaceChanges/<int:start>/<int:end>', views.reuplodeSpaceChanges),

]
