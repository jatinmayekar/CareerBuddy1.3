from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import asyncio
import websockets
import json
import base64
from pydub import AudioSegment
import io
import pyaudio
import wave
import cv2
from hume import HumeStreamClient
from hume.models.config import ProsodyConfig, FaceConfig
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://main--career-buddy.netlify.app", "http://localhost:3000"]}})

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUME_AI_API_KEY = os.getenv('HUME_AI_API_KEY')
HUME_AI_API_URL = "wss://api.hume.ai/v0/stream/evi"

# ... (keep existing routes and functions) ...

@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    data = request.json
    pitch_text = data.get('pitchText')
    
    # Use Hume AI API to convert text to speech
    audio_data = text_to_speech(pitch_text)
    
    return jsonify({"audioData": base64.b64encode(audio_data).decode('utf-8')})

@app.route('/analyze-practice', methods=['POST'])
def analyze_practice():
    audio_file = request.files.get('audio')
    video_file = request.files.get('video')
    
    # Process audio and video files
    audio_results = process_audio(audio_file)
    video_results = process_video(video_file)
    
    return jsonify({
        "audioAnalysis": audio_results,
        "videoAnalysis": video_results
    })

def text_to_speech(text):
    # Implement Hume AI text-to-speech conversion
    # This is a placeholder and needs to be implemented with actual Hume AI API calls
    return b"audio_data_placeholder"

def process_audio(audio_file):
    client = HumeStreamClient(HUME_AI_API_KEY)
    config = ProsodyConfig()
    
    result = asyncio.run(analyze_audio(client, config, audio_file))
    return aggregate_audio_results(result)

def process_video(video_file):
    client = HumeStreamClient(HUME_AI_API_KEY)
    config = FaceConfig()
    
    result = asyncio.run(analyze_video(client, config, video_file))
    return aggregate_video_results(result)

async def analyze_audio(client, config, audio_file):
    async with client.connect([config]) as socket:
        result = await socket.send_file(audio_file)
        return result["prosody"]["predictions"][0]["emotions"] if "prosody" in result else None

async def analyze_video(client, config, video_file):
    async with client.connect([config]) as socket:
        result = await socket.send_file(video_file)
        return result["face"]["predictions"] if "face" in result else None

def aggregate_audio_results(results):
    if not results:
        return {"error": "No valid results to aggregate."}
    
    all_emotions = {}
    for emotion in results:
        name = emotion['name']
        score = emotion['score']
        all_emotions[name] = all_emotions.get(name, []) + [score]
    
    avg_emotions = {name: np.mean(scores) for name, scores in all_emotions.items()}
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    
    return {"topEmotions": sorted_emotions[:5]}

def aggregate_video_results(results):
    if not results:
        return {"error": "No valid video results to aggregate."}
    
    all_emotions = {}
    for frame in results:
        if 'emotions' in frame:
            for emotion in frame['emotions']:
                name = emotion['name']
                score = emotion['score']
                all_emotions[name] = all_emotions.get(name, []) + [score]
    
    avg_emotions = {name: np.mean(scores) for name, scores in all_emotions.items()}
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    
    return {"topEmotions": sorted_emotions[:5]}

if __name__ == '__main__':
    app.run(debug=True)