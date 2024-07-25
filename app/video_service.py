from flask import Blueprint, request, jsonify
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import tempfile

video_blueprint = Blueprint('video', __name__)

@video_blueprint.route('/video-to-text', methods=['POST'])
def video_to_text():
    file = request.files['file']
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp_file.name)
    
    video = VideoFileClip(temp_file.name)
    audio = video.audio
    audio_file = 'temp.wav'
    audio.write_audiofile(audio_file)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

    # Optionally save the result to patient info
    # patient_info.update({'video_text': text})

    return jsonify({'text': text})
