from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import openai
import PyPDF2
import io
import traceback
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from functools import wraps
import json
import traceback
from huggingface_hub import InferenceClient


app = Flask(__name__)
CORS(app, resources={
     r"/*": {"origins": ["https://main--career-buddy.netlify.app", "http://localhost:3000"]}})

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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

# Add home route


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
            user_trials[user_id] -= 1
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

        # if pitches == []
        
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


if __name__ == '__main__':
    app.run(debug=True)
