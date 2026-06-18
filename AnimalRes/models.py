from django.db import models


# Create your models here.
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


class RescueLocation(BaseModel):
    name = models.CharField(max_length=120, unique=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Rescuers(BaseModel):
    USER_TYPE_CHOICES = [
        ("normal", "Normal User"),
        ("location_admin", "Location Admin"),
    ]

    userName = models.CharField(max_length=100, unique=True)
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPE_CHOICES,
        default="normal",
    )
    location = models.ForeignKey(
        RescueLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescuers",
    )

    def __str__(self):
        return self.userName


class Animal(BaseModel):
    animal = models.CharField(max_length=100, null=True)
    pic_url = models.CharField(max_length=1000,null=True)

    def __str__(self):
        return self.animal or "Animal"


class AnimalRescued(BaseModel):
    location = models.ForeignKey(
        RescueLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rescues",
    )
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
    ai_pickup_review = models.TextField(null=True, blank=True)
    ai_release_review = models.TextField(null=True, blank=True)
    ai_risk_level = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.animal or 'Animal'} rescue #{self.id}"
