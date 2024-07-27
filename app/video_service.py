from fastapi import APIRouter, UploadFile, File, HTTPException
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import tempfile
import os

router = APIRouter()

@router.post("/video-to-text")
async def video_to_text_service(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('video'):
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Save the uploaded file to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as f:
            f.write(await file.read())

        # Extract audio from the video file
        video = VideoFileClip(temp_file.name)
        audio = video.audio
        audio_file = 'temp.wav'
        audio.write_audiofile(audio_file)

        # Use SpeechRecognition to transcribe the audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Clean up temporary files
        os.remove(temp_file.name)
        os.remove(audio_file)

        return {"text": text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
