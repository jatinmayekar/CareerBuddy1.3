from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import openai
import PyPDF2
import io
import traceback
import os
import asyncio
import websockets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
import requests
from functools import wraps
import traceback
from huggingface_hub import InferenceClient
import tempfile
from werkzeug.utils import secure_filename
import logging
import time
from functools import wraps

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://career-buddy.netlify.app/", "http://localhost:3000"]}})

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUME_AI_API_KEY = os.getenv('HUME_AI_API_KEY')
HUME_AI_API_URL = "wss://api.hume.ai/v0/stream/evi"

API_KEY = os.getenv("HUME_AI_API_KEY")
API_URL = "wss://api.hume.ai/v0/evi/chat"

API_TYPE = ""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

debugLevel = 3 # Debugging level : 3 for in-depth

# In-memory storage for demo purposes. Replace with a database in production.
user_trials = {}

SYSTEM_PROMPT = """Generate three distinct, concise, and compelling career fair pitches (each 30-60 seconds when spoken) based on the candidate's resume and the job description. Each pitch should:

1. Introduce the candidate and their relevant experience
2. Highlight key skills and achievements
3. Show alignment with the job and company
4. Invite further discussion

Ensure each pitch has a unique approach or emphasizes different aspects of the candidate's background.

Tailor each pitch to the specific resume and job description provided, ensuring they're brief yet impactful.

Must format your response exactly as follows:

[PITCH1]
(Content of first pitch here)
[/PITCH1]

[PITCH2]
(Content of second pitch here)
[/PITCH2]

[PITCH3]
(Content of third pitch here)
[/PITCH3]

"""

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.exception(f"All retry attempts failed for {func.__name__}")
                        raise
                    else:
                        wait = backoff_in_seconds * 2 ** x
                        logger.warning(f"Attempt {x + 1} failed for {func.__name__}: {str(e)}. Retrying in {wait} seconds...")
                        time.sleep(wait)
                        x += 1
        return wrapper
    return decorator

def validate_api_key(api_key):
    client = OpenAI(api_key=api_key)
    try:
        print(client.models.list())
        return True
    except Exception as e:
        print(f"API Key Validation Error: {str(e)}")
        return False

def extract_text_from_pdf(pdf_file):
    print("Extracting pdf")
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        #if debugLevel == 3:
        #print("Extracted text:", text[:100])
        return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None

@retry_with_backoff(retries=3)
def generate_pitches_hf(hf_token, model_name, resume, job_description):
    print(f"Received HF API key: {hf_token[:5]}...") # Print first 5 characters for security
    try:
        client = InferenceClient(
            model=model_name,
            token=hf_token,
        )

        prompt = f"{SYSTEM_PROMPT}\n\nResume:\n{resume}\n\nJob Description:\n{job_description}\n\nGenerate the pitches:"

        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            stream=False,
        )

        full_response = response.choices[0].message.content

        pitches = []
        for i in range(1, 4):
            start = full_response.find(f"[PITCH{i}]") + len(f"[PITCH{i}]")
            end = full_response.find(f"[/PITCH{i}]")
            if start != -1 and end != -1:
                pitches.append(full_response[start:end].strip())

        return pitches
    except Exception as e:
        print(f"Error generating pitches with Hugging Face: {str(e)}")
        print(traceback.format_exc())
        return [f"Error: {str(e)}"]

@retry_with_backoff(retries=3)
def generate_pitches_openai(api_key, resume, job_description):
    client = OpenAI(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume:\n{resume}\n\nJob Description:\n{job_description}"}
            ]
        )
        content = chat_completion.choices[0].message.content
        pitches = []
        for i in range(1, 4):
            start = content.find(f"[PITCH{i}]") + len(f"[PITCH{i}]")
            end = content.find(f"[/PITCH{i}]")
            if start != -1 and end != -1:
                pitches.append(content[start:end].strip())
        return pitches
    except Exception as e:
        print(f"Error generating pitches with OpenAI: {str(e)}")
        return [f"Error: {str(e)}"]

@app.route('/')
def home():
    return "Welcome to CareerBuddy API!"

@app.route('/validate-api-key', methods=['POST'])
def api_validate_api_key():
    print("Received request to validate API key")
    data = request.json
    print(f"Request data: {data}")
    api_key = data.get('apiKey', '')

    if not api_key:
        print("No API key provided")
        return jsonify({"error": "API key is required"}), 400

    print("Validating API key")
    is_valid = validate_api_key(api_key)
    print(f"API key is valid: {is_valid}")
    return jsonify({"isValid": is_valid})

@app.route('/generate-pitches', methods=['POST'])
def api_generate_pitches():
    try:
        #print("Request form data:", request.form)
        #print("Request files:", request.files)
        
        # Don't try to access request.json for multipart form data
        if request.content_type.startswith('multipart/form-data'):
            data = request.form
        elif request.is_json:
            data = request.json
        else:
            return jsonify({"error": "Unsupported Media Type"}), 415

        resume = ''
        job_description = ''
        is_trial_mode = data.get('isTrialMode') == 'true'
        api_type = data.get('apiType', 'openai')
        API_TYPE = api_type
        user_api_key = data.get('apiKey', '')
        user_id = data.get('userId', '')
        model_name = data.get('modelName', 'meta-llama/Meta-Llama-3-8B-Instruct')

        print(f"Received API Type: {api_type}")
        print(f"Received API key (first 5 chars): {user_api_key[:5]}...")

        # Handle file uploads for resume
        if 'resumeFile' in request.files:
            pdf_file = request.files['resumeFile'].read()
            resume_text = extract_text_from_pdf(pdf_file)
            if resume_text is None:
                return jsonify({"error": "Failed to read resume PDF file"}), 400
            resume = resume_text
        elif 'resume' in data:
            resume = data.get('resume', '')

        # Handle file uploads for job description
        if 'jobDescriptionFile' in request.files:
            pdf_file = request.files['jobDescriptionFile'].read()
            job_description_text = extract_text_from_pdf(pdf_file)
            if job_description_text is None:
                return jsonify({"error": "Failed to read job description PDF file"}), 400
            job_description = job_description_text
        elif 'jobDescription' in data:
            job_description = data.get('jobDescription', '')

        if not resume or not job_description:
            return jsonify({"error": "Both job description and resume are required"}), 400

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Initialize user trials if not exists
        if user_id not in user_trials:
            user_trials[user_id] = 3

        #print(f"user trials: {user_trials[user_id]}\n")
        if is_trial_mode:
            if user_trials[user_id] <= 0:
                return jsonify({"error": "Free trials are exhausted. Please provide your own API key."}), 403
            api_key = OPENAI_API_KEY
            api_type = 'openai'
        else:
            api_key = user_api_key

        # Generate pitches based on API type
        if api_type == 'openai':
            pitches = generate_pitches_openai(api_key, resume, job_description)
        elif api_type == 'hf':
            pitches = generate_pitches_hf(api_key, model_name, resume, job_description)
        else:
            return jsonify({"error": "Invalid API type"}), 400

        # Only decrement trial if pitches were successfully generated
        if is_trial_mode and pitches != []:
            user_trials[user_id] -= 1

        return jsonify({
            "pitches": pitches, 
            "trialsRemaining": max(0, user_trials[user_id])
        })
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/submit-investor-form', methods=['POST'])
def submit_investor_form():
    try:
        data = request.json
        name = data.get('name')
        sender_email = data.get('email')
        interest = data.get('interest')
        reason = data.get('reason')
        amount = data.get('amount')

        # Create email content
        subject = f"New {interest.capitalize()} Interest in CareerBuddy"
        body = f"""
        New {interest} interest from:

        Name: {name}
        Email: {sender_email}
        Interest: {interest.capitalize()}
        Reason: {reason}
        """

        if interest in ['investing', 'both']:
            body += f"Potential Investment Amount: {amount}\n"

        # Your Gmail configuration
        your_email = "jatinmayekar27@gmail.com"  # Replace with your Gmail address
        # We'll set this as an environment variable
        app_password = os.environ.get('GMAIL_APP_PASSWORD')

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email  # Use the email from the form
        message["To"] = your_email
        message["Subject"] = subject
        # Set reply-to as the sender's email
        message["Reply-To"] = sender_email

        message.attach(MIMEText(body, "plain"))

        # Send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(your_email, app_password)
            server.send_message(message)

        return jsonify({"message": "Form submitted successfully"}), 200
    except Exception as e:
        print(f"Error submitting investor form: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        
@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    data = request.json
    pitch_text = data.get('pitchText')
    
    if not pitch_text:
        return jsonify({"error": "No pitch text provided"}), 400

    try:
        audio_data, text_response = asyncio.run(generate_audio_async(pitch_text))
        
        if audio_data:
            return jsonify({
                "audioData": base64.b64encode(audio_data).decode('utf-8'),
                "textResponse": text_response
            })
        else:
            return jsonify({"error": text_response}), 500

    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return jsonify({"error": str(e)}), 500

async def generate_audio_async(pitch_text):
    try:
        websocket = await connect_to_evi()
        if not websocket:
            return None, "Failed to connect to Hume AI EVI Chat API"

        await send_message(websocket, pitch_text)
        audio_data, text_response = await receive_audio(websocket)
        await websocket.close()

        return audio_data, text_response
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return None, str(e)
    
async def send_message(websocket, message):
    assistant_input = {
        "type": "assistant_input",
        "text": message
    }
    await websocket.send(json.dumps(assistant_input))
    print(f"Message sent: {message}")

async def receive_audio(websocket):
    print("Waiting for audio response...")
    audio_chunks = []
    text_response = ""
    
    try:
        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received response of type: {data['type']}")
            
            if data["type"] == "audio_output":
                audio_chunks.append(base64.b64decode(data["data"]))
            elif data["type"] == "assistant_message":
                text_response += data['message']['content'] + " "
            elif data["type"] == "assistant_end":
                print("Received end of assistant response")
                break
            else:
                print(f"Received other message type: {data['type']}")
    
    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed unexpectedly. The complete message may not have been received.")
    
    if audio_chunks:
        combined_audio = AudioSegment.empty()
        for chunk in audio_chunks:
            segment = AudioSegment.from_wav(io.BytesIO(chunk))
            combined_audio += segment
        
        audio_data = combined_audio.export(format="wav").read()
        return audio_data, text_response
    else:
        print("No audio data received")
        return None, text_response
    
async def connect_to_evi(max_retries=3, retry_delay=5):
    uri = f"{API_URL}?api_key={API_KEY}"
    for attempt in range(max_retries):
        try:
            websocket = await websockets.connect(uri)
            print("Connected to Hume AI EVI Chat API")
            return websocket
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to connect.")
    return None

async def close_connection(websocket):
    if websocket:
        await websocket.close()
        logger.debug("WebSocket connection closed")

@app.route('/analyze-practice', methods=['POST'])
def analyze_practice():
    try:
        audio_file = request.files.get('audio')
        video_file = request.files.get('video')
        
        if not audio_file or not video_file:
            return jsonify({"error": "Both audio and video files are required"}), 400

        logger.debug(f"Received audio file: {audio_file.filename}")
        logger.debug(f"Received video file: {video_file.filename}")

        # Process audio and video files
        audio_results = process_audio(audio_file)
        video_results = process_video(video_file)
        
        return jsonify({
            "audioAnalysis": audio_results,
            "videoAnalysis": video_results
        })
    except Exception as e:
        logger.exception("Error in analyze_practice")
        return jsonify({"error": str(e)}), 500

def process_audio(audio_file):
    client = HumeStreamClient(HUME_AI_API_KEY)
    config = ProsodyConfig()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        audio_file.save(temp_audio)
        temp_audio_path = temp_audio.name

    try:
        result = asyncio.run(analyze_audio(client, config, temp_audio_path))
        return aggregate_audio_results(result)
    finally:
        os.unlink(temp_audio_path)  # Delete the temporary file

def process_video(video_file):
    client = HumeStreamClient(HUME_AI_API_KEY)
    config = FaceConfig()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        video_file.save(temp_video)
        temp_video_path = temp_video.name

    try:
        result = asyncio.run(analyze_video(client, config, temp_video_path))
        return aggregate_video_results(result)
    finally:
        os.unlink(temp_video_path)  # Delete the temporary file

async def analyze_audio(client, config, audio_file_path):
    async with client.connect([config]) as socket:
        result = await socket.send_file(audio_file_path)
        return result["prosody"]["predictions"][0]["emotions"] if "prosody" in result else None

async def analyze_video(client, config, video_file_path):
    async with client.connect([config]) as socket:
        result = await socket.send_file(video_file_path)
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

@retry_with_backoff(retries=3)
def generate_feedback_openai(api_key, analysis_results):
    client = OpenAI(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You must be an expert career coach providing feedback on a practice pitch concisely, smartly and efficiently based on the pitch analysis scores. You must reply as if you are directly talking to the user"},
                {"role": "user", "content": f" Pitch analysis: {analysis_results}"}
            ]
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.exception("Error generating feedback with OpenAI")
        raise  # Re-raise the exception to trigger the retry

@retry_with_backoff(retries=3)
def generate_feedback_hf(api_key, model_name, analysis_results):
    client = InferenceClient(
        model=model_name,
        token=api_key,
    )
    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You must be an expert career coach providing feedback on a practice pitch concisely, smartly and efficiently based on the pitch analysis scores. You must reply as if you are directly talking to the user"},
                {"role": "user", "content": f" Pitch analysis: {analysis_results}"}
            ],
            max_tokens=1000,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception("Error generating feedback with Hugging Face")
        raise  # Re-raise the exception to trigger the retry

@app.route('/generate-feedback', methods=['POST'])
def generate_feedback():
    try:
        data = request.json
        analysis_results = data.get('analysisResults')
        is_trial_mode = data.get('isTrialMode') == 'true'
        api_type = data.get('apiType', 'openai')
        user_api_key = data.get('apiKey', '')
        user_id = data.get('userId', '')
        model_name = data.get('modelName', 'meta-llama/Meta-Llama-3-8B-Instruct')

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        if is_trial_mode:
            if user_trials[user_id] <= 0:
                return jsonify({"error": "Free trials are exhausted. Please provide your own API key."}), 403
            api_key = OPENAI_API_KEY
            api_type = 'openai'
        else:
            api_key = user_api_key

        if api_type == 'openai':
            feedback = generate_feedback_openai(api_key, analysis_results)
        elif api_type == 'hf':
            feedback = generate_feedback_hf(api_key, model_name, analysis_results)
        else:
            return jsonify({"error": "Invalid API type"}), 400

        if not feedback:
            return jsonify({"error": "Failed to generate feedback"}), 500

        return jsonify({"feedback": feedback})
    except Exception as e:
        logger.exception("Error in generate_feedback")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True)