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
from .utils import *
from .response import *
from api.user.models import *


# API FOR CHECK STATUS
class UserFreeTRailStausView(APIView):
    def post(self, request, format=None):

        try: 
            # Get email from request
            email = request.data.get("email")
            if not email:
                return BAD_REQUEST_RESPONSE("Email is required. Please provide it using the key 'email'.")
            
            # Get user object
            user_obj = User.objects.filter(email=email).first()

            if not user_obj:
                return NOT_FOUND_RESPONSE("User not found")

            # Get subscription status and file count
            is_paid = user_obj.subscription_status
            file_count = user_obj.file_upload_count or 0  # Handle None safely

            # Check trial limit
            if file_count > 5 and not is_paid:
                return FREE_TRAIL_EXPIRED_RESPONSE(False ,"Your free trial limit has expired" )
            
            # if free trial is pending
            return TRAIL_PENDING(True ,  "Trial access is valid")

        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to upload image error occur {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)


class RecognizeImage(APIView):
    def post(self ,request , format=None):
        sheet_music_data = []
        sheet_midi_data = []
        sheet_wav_data = []

        try:
            email = request.data.get("email")
            original_image = request.FILES.get("photo_img")
            selectedImageURL = request.FILES.getlist("selectedImageURL")

            # Email not found handling 
            if not email:
                return BAD_REQUEST_RESPONSE("Email is required. Please provide it using the key 'email'.")

            if not original_image:
                return BAD_REQUEST_RESPONSE("original image is required. Please provide it using the key 'photo_img'.")

                    
            # # Initialize a list to store the recognized sheet music data
            if not selectedImageURL:
                return BAD_REQUEST_RESPONSE("Please upload an image before proceeding.")

            
            # Get user object
            user_obj = User.objects.filter(email=email).first()
            res = ImageEditingTrack(user_obj , original_image, selectedImageURL)

            OriginalFileCount = OriginalImageTrack(user_obj , original_image)
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
                    "data": response_dict
                      
                    })

        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to upload image error occur {str(e)} at line {exc_tb.tb_lineno}'
            return InternalServer_Response(error_messsage)
        

"""
class RecognizeImage(APIView):
    def post(self ,request , format=None):
        sheet_music_data = []
        sheet_midi_data = []
        sheet_wav_data = []

        try:

            selectedImageURL = request.FILES.getlist("selectedImageURL")
            # Initialize a list to store the recognized sheet music data

            if not selectedImageURL:
                return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Please upload an image before proceeding."
                    })

            idx = 0
            # Iterate through each uploaded image
            for image_obj in selectedImageURL:
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
                    "data": response_dict
                      
                    })

        except Exception as e:
            exc_type , exc_obj , exc_tb = sys.exc_info()
            error_messsage = f'failed to upload image error occur {str(e)} at line {exc_tb.tb_lineno}'
            return Response({
                "satus": status.HTTP_500_INTERNAL_SERVER_ERROR , 
                "message": error_messsage,
            })



"""