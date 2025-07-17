from django.http import JsonResponse
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


def recognize_image(request):
    if request.method == "POST":
        selectedImageURL = request.FILES.getlist("selectedImageURL")

        # Initialize a list to store the recognized sheet music data
        sheet_music_data = []
        sheet_midi_data = []
        sheet_wav_data = []

        idx = 0
        # Iterate through each uploaded image
        for image_obj in selectedImageURL:
            idx = idx + 1
            image = Image.open(image_obj).convert("L")
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

        return JsonResponse(
            {
                "status": True,
                "file_count": len(selectedImageURL),
                "sheet_music_data": sheet_music_data,
                "sheet_midi_data": sheet_midi_data,
                "sheet_wav_data": sheet_wav_data,  # Include the MP3 file paths in the response
            }
        )

    else:
        return JsonResponse({"status": False, "error": "Invalid request method"})
