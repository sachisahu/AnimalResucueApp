import random
import string
import requests
import json
from  AnimalResucueApp import settings
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile


def uploadResourcesToDigitalOcean(folderName, file):
    from storages.backends.s3boto3 import S3Boto3Storage

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


def generate_demo_ai_review(animal, status, landmark=None, phase="pickup"):
    status = (status or "Unknown").strip()
    animal = (animal or "animal").strip()
    landmark_text = f" near {landmark}" if landmark else ""
    color_map = {
        "Dog": "brown and white",
        "Cat": "grey and white",
        "Cow": "black and white",
        "Bird": "dark feathered",
        "Monkey": "brown",
    }
    visible_color = color_map.get(animal, "light brown")

    risk_map = {
        "Normal": "Low",
        "Cured": "Low",
        "Sick": "Medium",
        "Critical": "High",
        "Died": "Critical",
    }
    risk_level = risk_map.get(status, "Medium")

    if phase == "release":
        if status == "Cured":
            comment = (
                f"AI visual review: the {animal} appears {visible_color}, alert, and stable in the release photo{landmark_text}. "
                "Body posture looks improved, no major fresh bleeding is visible, and the surroundings look suitable for release. "
                "Recommendation: mark as cured after final staff confirmation."
            )
        elif status == "Died":
            comment = (
                f"AI visual review: the {animal} appears {visible_color} and non-responsive in the release/update photo{landmark_text}. "
                "The case should be treated as critical documentation, with medical notes and rescue timeline verified by an admin. "
                "Recommendation: keep this record flagged for closure review."
            )
        else:
            comment = (
                f"AI visual review: the {animal} appears {visible_color} but still shows signs of stress or weakness{landmark_text}. "
                "The animal may not be ready for final release based on the selected status and visible condition cues. "
                "Recommendation: continue observation and require location admin approval."
            )
    else:
        if status == "Critical":
            comment = (
                f"AI visual review: the rescued {animal} appears {visible_color} with visible distress indicators{landmark_text}. "
                "The posture and reported condition suggest possible injury, shock, or severe weakness at the pickup spot. "
                "Recommendation: urgent medical triage, keep the exact location attached, and prioritize transport."
            )
        elif status == "Sick":
            comment = (
                f"AI visual review: the {animal} appears {visible_color} and may be sick or dehydrated{landmark_text}. "
                "The selected condition and image context suggest reduced mobility or fatigue at the rescue spot. "
                "Recommendation: veterinary observation, hydration check, and wound/mobility assessment."
            )
        else:
            comment = (
                f"AI visual review: the {animal} appears {visible_color} and relatively stable in the pickup image{landmark_text}. "
                "No severe distress is indicated by the selected status, but the case should still be documented with location proof. "
                "Recommendation: verify species, visible injuries, and surrounding hazards during admin review."
            )

    return comment, risk_level
