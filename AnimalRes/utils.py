import random
import string
import requests
import json
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from  AnimalResucueApp import settings
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


def uploadResourcesToDigitalOcean(folderName, file):
    storage = S3Boto3Storage()
    image_path = f"resources/{str(folderName)}/{str(generate_random_alphanumeric(40))}{file.name}"
    storage.save(image_path, file)
    fileUrl = "https://animalrescuesresources-space.blr1.digitaloceanspaces.com/resources/" + str(image_path)
    return fileUrl


def generate_random_alphanumeric(length):
    alphanumeric_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric_chars) for _ in range(length))


def moveImages(oldURL,folderName):
    try:
        # Download the image from the URL
        response = requests.get(oldURL)
        response.raise_for_status()  # Raise an error on bad status

        # Prepare the image file in-memory
        image_bytes = BytesIO(response.content)
        image_name = oldURL.split('/')[-1]  # Attempt to preserve the original file name
        file = ImageFile(image_bytes, name=image_name)

        # Call your function to upload the image to DigitalOcean
        new_url = uploadResourcesToDigitalOcean(folderName, file)
        return new_url
    except requests.RequestException as e:
        print(f"Failed to download image from {oldURL}. Error: {e}")
        return None
