# Generated for demo role-based permissions.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("AnimalRes", "0009_location_and_ai_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="rescuers",
            name="user_type",
            field=models.CharField(
                choices=[
                    ("normal", "Normal User"),
                    ("location_admin", "Location Admin"),
                ],
                default="normal",
                max_length=30,
            ),
        ),
    ]
