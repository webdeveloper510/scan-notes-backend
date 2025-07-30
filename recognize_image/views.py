from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
import base64
from .preprocessing import predict, sound_midi
from PIL import Image
import tensorflow as tf
import cv2
from PIL import Image
import numpy as np
import tempfile
import uuid
import os
from music21 import converter
from midi2audio import FluidSynth
import sys
from rest_framework.views import APIView
from .thrive import *
from .response import *
from api.user.models import *
from rest_framework.permissions import IsAuthenticated
from api.user.serializers import EditUserHistorySerializer
from core.settings import MEDIA_ROOT , BASE_URL, HOST
from .utils import generate_random_string ,OriginalImageTrack ,ImageEditingTrack

# API FOR CHECK STATUS
class UserFreeTRailStausView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        try: 
            # Get email from request
            #email = request.data.get("email")                          # for local    
            email = request.user.email                                  # for live

            # Get user object
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return NOT_FOUND_RESPONSE("User not found")

            # Get subscription status and file count
            is_paid = user_obj.subscription_status
            file_count = user_obj.file_upload_count or 0  # Handle None safely
            payment_status =""

            # filter put payment details
            payment_obj = PaymentDetails.objects.filter(user_id= user_obj.id).first()

            if not payment_obj:
                payment_status = False

            else:
                payment_status = payment_obj.payment_status

            # Check trial limit
            if file_count >=5 and not is_paid:
                message = "You have active subscription " if payment_status == "order.success" else "Your free trial limit has expired"
                return FREE_TRAIL_EXPIRED_RESPONSE(False , payment_status,message)
            
            # if free trial is pending
            message = "You have active subscription " if payment_status == "order.success" else  "Trial access is valid"
            return TRAIL_PENDING(True ,payment_status ,  message)

        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to upload image error occur {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)

class RecognizeImage(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self ,request , format=None):
        sheet_music_data = []
        sheet_midi_data = []
        sheet_wav_data = []

        try:
            #email = request.data.get("email")                         # for local
            email = request.user.email                                  # for live

            # GET POST DATA
            object_id = request.data.get("object_id")
            original_image = request.FILES.get("photo_img")
            selectedImageURL = request.FILES.getlist("selectedImageURL")

            if not object_id:
                return BAD_REQUEST_RESPONSE("Object ID is required. Please provide it using the key 'object_id'.")

            if not original_image:
                return BAD_REQUEST_RESPONSE("original image is required. Please provide it using the key 'photo_img'.")

            # Initialize a list to store the recognized sheet music data
            if selectedImageURL:

                # Get user object
                object_id = int(object_id) if object_id else 0
                user_obj = User.objects.filter(email=email).first()
                if not user_obj:
                    return BAD_REQUEST_RESPONSE("Invalid user email")
                
                OriginalFileCount = 0
                original_image_url = None
                if object_id == 0:
                    OriginalFileCount, original_image_url = OriginalImageTrack(user_obj , original_image)
                
                elif selectedImageURL is None and object_id > 0:
                    #Reuse existing image URL from DB
                    crop_history_obj = CropImageHistoryModel.objects.filter(id=object_id).first()
                    if not crop_history_obj:
                        return BAD_REQUEST_RESPONSE("Invalid object ID provided")
                    
                    original_image_url = crop_history_obj.orignal_image  # spelling preserved from your model

                # call to function for save crop images
                Crop_table_object_id = ImageEditingTrack(object_id, user_obj , original_image_url, selectedImageURL)
                idx = 0
                
                #Iterate through each uploaded image
                for image_obj in selectedImageURL:
                    print('image object ', image_obj)
                    idx = idx + 1
                    image = Image.open(image_obj).convert("L")          # Convert image into grayscale
                    image_array = np.array(image)

                    ret, thresh = cv2.threshold(
                        image_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                    )
                    cv2.imwrite("image.png", thresh)
                    Result = predict(thresh)

                    
                    Result_str = ""  # text of music sheet
                    for i in Result:
                        note_str = str(i)
                        Result_str = Result_str + note_str + " , "

                    # print(Result_str)
                    sheet_music_data.append(Result_str)

                    Midi = sound_midi(Result)  # midi of music sheet
                    # Save the MIDI file
                    output_mid = str(uuid.uuid4()) + ".mid"

                    output_path = os.path.join("media", output_mid)

                    with open(output_path, "wb") as output_file:
                        Midi.writeFile(output_file)

                    sheet_midi_data.append(output_path)

                    # Convert MIDI to WAV using FluidSynth
                    wav_output = str(uuid.uuid4()) + ".wav"
                    wav_output_path = os.path.join("media", wav_output)

                    soundfont_file = os.path.join(
                        os.getcwd(), "recognize_image", "sound_font.sf2"
                    )

                    fluidsynth = FluidSynth(sound_font=soundfont_file)
                    fluidsynth.midi_to_audio(output_path, wav_output_path)

                    sheet_wav_data.append(wav_output_path)

                    response_dict ={
                        "status": True,
                        "file_count": len(selectedImageURL),
                        "sheet_music_data": sheet_music_data,
                        "sheet_midi_data": sheet_midi_data,
                        "sheet_wav_data": sheet_wav_data,  # Include the MP3 file paths in the response
                    }

                    # Return Response
                    return Response({
                        "status"  : status.HTTP_200_OK,
                        "user_file_track": OriginalFileCount,
                        "object_id": Crop_table_object_id,
                        "data": response_dict
                        
                        })
            
            else:
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "No any action perform"
                })
        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to upload image error occur {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)
        

# API FOR GET HISTORY 
class UserImagesHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        try:
            # Get email from request
            #email = request.data.get("email")                 # FOR Local
            email = request.user.email                          # FOR live
            
            # Get user object
            user_obj = User.objects.filter(email=email).first()

            # Filter out crop data
            user_history_obj = CropImageHistoryModel.objects.filter(user_id =user_obj.id).all().values()

            if not user_history_obj:
                return NOT_FOUND_RESPONSE("User  haven't uploaded any cropped images yet.")
            
            import pandas as pd
            df = pd.DataFrame(list(user_history_obj))
            
            sorted_df = df.sort_values(by=['title', 'COMPOSER'])

            json_output = sorted_df.to_dict(orient="records") if not sorted_df.empty else []

            return Response({
                "status": status.HTTP_200_OK ,
                "data": json_output
            })

        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to get user history,  error occur {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)


# API FOR EDIT HISTORY 
class EditUserHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, format=None):
        try:
            object_id = request.data.get("obj_id")
            new_images_obj = request.FILES.getlist("newCropImages")

            if not object_id:
                return Response({"message": "Object Id is required. Please provide it using the key 'obj_id'."})

            user_history_obj = CropImageHistoryModel.objects.filter(id=object_id).first()
            if not user_history_obj:
                return NOT_FOUND_RESPONSE("No Object found with ID: {}".format(object_id))

            file_array = user_history_obj.crop_images or []

            # Save new files
            original_image_dir = os.path.join(MEDIA_ROOT, "crop_images", request.user.first_name)
            os.makedirs(original_image_dir, exist_ok=True)

            if new_images_obj:
                for file in new_images_obj:
                    random_name = generate_random_string(5)
                    crop_file_name = f"{file.name}-{random_name}"
                    file_path = os.path.join(original_image_dir, crop_file_name)
                    file_url = file_path.replace(MEDIA_ROOT, BASE_URL)

                    # Replace existing file
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)

                    file_array.append({
                        "file_name": file.name,
                        "file_url": file_url
                    })

                user_history_obj.crop_images = file_array
                user_history_obj.save()

            json_data = EditUserHistorySerializer(user_history_obj).data
            return Response({"status": status.HTTP_200_OK, "data": json_data})

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"Failed to update object, error: {str(e)} at line {exc_tb.tb_lineno}"
            return InternalServer_Response(error_message)


# API FOR DELETE HISTORY 
class DeleteUserHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, format=None):
        try:
            object_id = request.data.get("obj_id", None)
            object_delete_status = request.data.get("status", False)
            crop_obj_urls = request.data.get("objects_urls", [])

            if not object_id:
                return Response({
                    "message": "Object Id is required. Please provide ids array using the key 'obj_id'."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not crop_obj_urls:
                return Response({
                    "message": "crop_obj_urls is required. Please provide it using the key 'objects_urls'."
                }, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(crop_obj_urls, list):
                return Response({
                    "error": "crop_obj_urls must be a list."
                }, status=status.HTTP_400_BAD_REQUEST)

            user_history_obj = CropImageHistoryModel.objects.filter(id=object_id).first()
            if not user_history_obj:
                return NOT_FOUND_RESPONSE("No Object found with ID: {}".format(object_id))

            # If object_delete_status is True, delete the entire object
            if object_delete_status:
                user_history_obj.delete()
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "Object and all crop images deleted successfully."
                })

            # If only crop images need to be deleted
            crop_data_array = user_history_obj.crop_images or []
            if crop_data_array:
                import pandas as pd

                df = pd.DataFrame(crop_data_array)
                df = df[~df['file_url'].isin(crop_obj_urls)]  # Delete matching URLs

                user_history_obj.crop_images = df.to_dict(orient="records")
                user_history_obj.save()

            json_data = EditUserHistorySerializer(user_history_obj).data
            return Response({"status": status.HTTP_200_OK, "data": json_data})
        

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"Failed to update object, error: {str(e)} at line {exc_tb.tb_lineno}"
            return InternalServer_Response(error_message)

# API TP UPDATE TITLE AND COMPOSER 
class WriteTitleComposerView(APIView):

    permission_classes= (IsAuthenticated ,)

    def post(self, request, format=None):
        try:
            payload = request.data

            # Handle missing field
            required_fields = ["object_id", "title", "composer"]
            missing_fields = [field for field in required_fields if not payload.get(field)]
            if missing_fields:
                return BAD_REQUEST_RESPONSE(f'Missing required field(s): {",".join(missing_fields)}')

            # filter out object from database
            history_obj = CropImageHistoryModel.objects.filter(id=payload.get("object_id")).first()
            if not history_obj:
                return NOT_FOUND_RESPONSE(f"Invalid Object ID: {payload.get('object_id')}")

            # save new data in database
            history_obj.title = payload["title"]
            history_obj.COMPOSER = payload["composer"]
            history_obj.save()

            # Serialize updated object
            serialized_data = EditUserHistorySerializer(history_obj).data

            # Return Response
            return Response({
                "message": "success",
                "status": 200,
                "data": serialized_data
            })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = (
                f"Failed to add title and composer. Error: {str(e)} at line {exc_tb.tb_lineno}"
            )
            return InternalServer_Response(error_message)



# API FOR Thrive cart webhook payment
class ThriveCartWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Get data
            data = request.data
            event_type = data.get('event')
            customer = data.get('customer', {})
            currency = data.get('currency', {})
            order = data.get('order', {})

            thrive_customer_email = customer.get("email")
            subscription_id = ""
            subscription_status = ""

            mode = data.get('mode')                 # change to 'live' if HOST is production

            # Get subscription details
            response = get_subscription_id(thrive_customer_email, mode)
            if response and "subscriptions" in response:
                subscription_data = response.get("subscriptions")
                subscription_id = subscription_data[0]['subscription_id']
                subscription_status = subscription_data[0]['status']
            else:
                subscription_id = 0
                subscription_status = "cancelled"

            # print('subscription_id ', subscription_id)
            # print('subscription_status ', subscription_status)


            thrivecustomer_id = customer.get("id")
            thrive_customer_name = customer.get("name")
            thrive_customer_address = customer.get("address")

            order_id = order.get('id')
            invoice_id = order.get("invoice_id")
            frequency = order.get("future_charges", [{}])[0].get('frequency')
            amount = order.get("charges", [{}])[0].get('amount')
            start_date = order.get("date")
            payment_due = order.get("future_charges", [{}])[0].get('due')
            processor = order.get("processor")
            product_name = order.get("charges", [{}])[0].get("name")
            product_id = order.get("charges", [{}])[0].get('item_identifier')

            user_obj = User.objects.filter(email=thrive_customer_email).first()
            if not user_obj:
                return NOT_FOUND_RESPONSE(f"No user found with email: {thrive_customer_email}")

            # Create or update PaymentDetails object
            payment_obj, created = PaymentDetails.objects.update_or_create(
                user_id=user_obj.id,
                defaults={
                    "subscription_status": subscription_status,
                    'order_id': order_id,
                    'invoice_id': invoice_id,
                    "subscription_id": subscription_id,
                    'currency': currency,
                    'frequency': frequency,
                    'amount': amount,
                    "start_date": start_date,
                    'end_date': payment_due,
                    'thrivecustomer_id': thrivecustomer_id,
                    'thrive_customer_name': thrive_customer_name,
                    'thrive_customer_email': thrive_customer_email,
                    'thrive_customer_address': thrive_customer_address,
                    'processor': processor,
                    'product_name': product_name,
                    'product_id': product_id,
                    'event_type': event_type,
                    "mode": mode
                }
            )

            row_status = "created" if created else "updated"

            response_data = {
                "user_id": payment_obj.user.id,
                "payment_status": payment_obj.event_type,
                "row_status": row_status
            }

            return Response({
                "message": "Payment details saved",
                "status": status.HTTP_200_OK,
                "detail": response_data
            })

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"Failed to create payment object, error: {str(e)} at line {exc_tb.tb_lineno}"
            return InternalServer_Response(error_message)


# API FOR GET PAYMENT DATA
class PaymentDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self , request):
        try:
            usr_id = request.user.id
            #usr_id = request.data.get("id")

            payment_obj = PaymentDetails.objects.filter(user_id=usr_id).values()

            # handle payment object not found
            if not payment_obj:
                return NOT_FOUND_RESPONSE(f"User has not payment detail with id : {usr_id}")
            

            import pandas as pd
            df = pd.DataFrame(list(payment_obj))
   


            rename_columns= {
                "thrive_customer_name": "customer_name",
                "thrive_customer_email": "email",
                "frequency": "plan_type",
                "event_type": "payment_status", 
            }

            df.rename(columns=rename_columns, inplace=True)

            filtered_columns = ["customer_name", "email", "invoice_id", "start_date", "end_date", "amount" ,"currency", "plan_type", "payment_status", "subscription_status"]

            filtered_df = df[filtered_columns]

            filtered_df["amount"] =filtered_df["amount"].apply(lambda x: f"€{x}")
            
            json_output = filtered_df.to_dict(orient="records")

            # Return Response
            return Response({
                "message": "success",
                "status": 200,
                "data": json_output
            })
        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to get payment detail data,  {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)


# API FOR CANCEL SUBSCRIPTION
class CancelSubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            email = request.user.email
            #email = request.data.get("email")
            
            # filter out payment data 
            paymnet_obj = PaymentDetails.objects.filter(thrive_customer_email=email).first()

            if not paymnet_obj:
                return Response({
                    "success": False,
                    "message": f"No Subscription found related to email: {email}"
                }, status=status.HTTP_404_NOT_FOUND)

            subscription_status = paymnet_obj.subscription_status
            subscription_id = paymnet_obj.subscription_id
            order_id = paymnet_obj.order_id
            mode = paymnet_obj.mode

            if subscription_status == "active" and subscription_id not in [0 , "0", "None"]:
                cancel_response = cancel_subscription(order_id, subscription_id, mode)
                print("cancel_response ", cancel_response)
                
                if 'error' in cancel_response:
                    return Response({
                        "status":status.HTTP_400_BAD_REQUEST,
                        "success": False,
                        "message": cancel_response['error']
                    })

                # Optionally check cancel_response success here
                else:
                    paymnet_obj.subscription_status = "cancelled"
                    paymnet_obj.save()
                    return Response({
                        "success": True,
                        "message": cancel_response.get("message", "Subscription cancelled successfully."),
                        "subscription_status": paymnet_obj.subscription_status
                    }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "success": False,
                    "message": f"Subscription is already {subscription_status}.",
                    "subscription_status": subscription_status
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_message = f"Failed to cancel subscription: {str(e)} at line {exc_tb.tb_lineno}"
            return Response({
                "success": False,
                "message": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
