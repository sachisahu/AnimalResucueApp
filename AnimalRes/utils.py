import random
import string
import requests
import json
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from  AnimalResucueApp import settings


def uploadResourcesToDigitalOcean(folderName, file):
    storage = S3Boto3Storage()
    image_path = f"resources/{str(folderName)}/{str(generate_random_alphanumeric(5))}{file.name}"
    storage.save(image_path, file)
    fileUrl = "https://animalrescuesresources.blr1.digitaloceanspaces.com/" + str(image_path)
    return fileUrl


def generate_random_alphanumeric(length):
    alphanumeric_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric_chars) for _ in range(length))
