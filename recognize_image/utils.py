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


def OriginalImageTrack(user , original_image):
    try:

        # Processing POST data
        original_image_dir = os.path.join(MEDIA_ROOT, "Original_uploaded_dir", user.first_name)
        os.makedirs(original_image_dir, exist_ok=True)
        file_path = os.path.join(original_image_dir, original_image.name)
        FILE_URL = file_path.replace(MEDIA_ROOT, BASE_URL)

        # Check if file exists and remove it
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Replacing existing file: {file_path}")

        # Save the file
        with open(file_path, 'wb') as destination:
            for chunk in original_image.chunks():
                destination.write(chunk)

        #Create object in database
        ImageAnalysisModel.objects.create(
            user=user,
            original_image=original_image.name,
            file_url=FILE_URL,
        )

        # Increase user file_uploaded count
        user.file_upload_count += 1
        user.save()

        # Now get the updated count
        updated_file_count = user.file_upload_count
        return updated_file_count , FILE_URL
    
    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        error_message  = f"Failed to save data in model : {ImageAnalysisModel} , error occur {str(e)} in line {exc_tb.tb_lineno}"
        return error_message
    

def ImageEditingTrack(user , original_image_url , FileArray):
    try:
        # Define directory for cropped images
        original_image_dir = os.path.join(MEDIA_ROOT, "crop_images", user.first_name)
        os.makedirs(original_image_dir, exist_ok=True)

        file_data = []
        for file in FileArray:
            Name_parse = generate_random_string(5)
            crop_file_name = f"{file.name}-{Name_parse}"
            file_path = os.path.join(original_image_dir, crop_file_name)
            file_url = file_path.replace(MEDIA_ROOT, BASE_URL)

            # Replace existing file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Replacing existing file: {file_path}")

            # Save the new file
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            file_data.append({
                "file_name": file.name,
                "file_url": file_url
            })

        #Save crop history in DB
        CropImageHistoryModel.objects.create(
            user=user,
            orignal_image=original_image_url ,
            crop_images=file_data
        )

        return True

    except Exception as e:
        exc_type , exc_obj , exc_tb = sys.exc_info()
        error_message  = f"Failed to save data in ImageAnalysisModel model , error occur {str(e)} in line {exc_tb.tb_lineno}"
        return error_message