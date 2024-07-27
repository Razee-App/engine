from fastapi import APIRouter, UploadFile, File, HTTPException
import moviepy.editor as mp
import speech_recognition as sr
import tempfile

router = APIRouter()

@router.post("/video-to-text")
async def video_to_text(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('video'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file.seek(0)

        video = mp.VideoFileClip(temp_file.name)
        audio = video.audio
        audio_file = 'temp.wav'
        audio.write_audiofile(audio_file)

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Optionally save the result to patient info
        # patient_info.update({'video_text': text})

        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
