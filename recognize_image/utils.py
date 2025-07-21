import os
import sys
from api.user.models import ImageAnalysisModel , CropImageHistoryModel
from core.settings import MEDIA_ROOT , BASE_URL
import random 
import string


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def OriginalImageTrack(user, original_image):
    try:
        # Create directory path
        original_image_dir = os.path.join(MEDIA_ROOT, "Original_uploaded_dir", user.first_name)
        os.makedirs(original_image_dir, exist_ok=True)

        # File path and URL
        file_path = os.path.join(original_image_dir, original_image.name)
        FILE_URL = file_path.replace(MEDIA_ROOT, BASE_URL)

        # Replace existing file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Replacing existing file: {file_path}")

        # Save the uploaded file
        with open(file_path, 'wb') as destination:
            for chunk in original_image.chunks():
                destination.write(chunk)

        # Update or create record
        ImageAnalysisModel.objects.create(
            user=user,
            original_image=original_image.name,
            file_url = FILE_URL
        )

        # Update user upload count
        user.file_upload_count += 1
        user.save()

        return user.file_upload_count, FILE_URL

    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        error_message  = f"Failed to save data in model : {ImageAnalysisModel} , error occur {str(e)} in line {exc_tb.tb_lineno}"
        return error_message
    


def ImageEditingTrack(object_id, user, original_image_url, FileArray):
    try:
        original_image_dir = os.path.join(MEDIA_ROOT, "crop_images", user.first_name)
        os.makedirs(original_image_dir, exist_ok=True)

        file_data = []

        for file in FileArray:
            name_suffix = generate_random_string(5)
            crop_file_name = f"{file.name}-{name_suffix}"
            file_path = os.path.join(original_image_dir, crop_file_name)
            file_url = file_path.replace(MEDIA_ROOT, BASE_URL)

            # Save file
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            file_data.append({
                "file_name": original_image_url,
                "file_url": file_url
            })

        # Update existing history
        if object_id > 0:
            user_history_obj = CropImageHistoryModel.objects.filter(id=object_id).first()
            if user_history_obj:
                existing_data = user_history_obj.crop_images or []
                # Avoid duplicates
                new_data = [
                    item for item in file_data
                    if item['file_url'] not in [existing['file_url'] for existing in existing_data]
                ]
                if new_data:
                    user_history_obj.crop_images = existing_data + new_data
                    user_history_obj.save()
                return True

        # Create new record if object_id is 0 or not found
        CropImageHistoryModel.objects.create(
            user=user,
            orignal_image=original_image_url,
            crop_images=file_data
        )
        return True

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return f"Failed to save data in CropImageHistoryModel: {str(e)} at line {exc_tb.tb_lineno}"

