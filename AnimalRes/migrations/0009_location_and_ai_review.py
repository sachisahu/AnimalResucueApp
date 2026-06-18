# Generated for location-wise demo redesign.

from django.db import migrations, models
import django.db.models.deletion


def seed_locations(apps, schema_editor):
    RescueLocation = apps.get_model("AnimalRes", "RescueLocation")
    for name, city in [
        ("Hyderabad Rescue Center", "Hyderabad"),
        ("Bangalore Rescue Center", "Bangalore"),
        ("Chennai Rescue Center", "Chennai"),
    ]:
        RescueLocation.objects.get_or_create(name=name, defaults={"city": city})


class Migration(migrations.Migration):

    dependencies = [
        ("AnimalRes", "0008_auto_20231209_1110"),
    ]

    operations = [
        migrations.CreateModel(
            name="RescueLocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("city", models.CharField(blank=True, max_length=120, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="ai_pickup_review",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="ai_release_review",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="ai_risk_level",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="location",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="rescues", to="AnimalRes.rescuelocation"),
        ),
        migrations.AddField(
            model_name="rescuers",
            name="location",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="rescuers", to="AnimalRes.rescuelocation"),
        ),
        migrations.RunPython(seed_locations, migrations.RunPython.noop),
    ]
