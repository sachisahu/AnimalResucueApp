# Generated for base model timestamps and soft delete support.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("AnimalRes", "0010_rescuers_user_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="animal",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="animal",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="animal",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="animalrescued",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="rescuelocation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="rescuelocation",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="rescuelocation",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="rescuers",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="rescuers",
            name="is_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="rescuers",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
