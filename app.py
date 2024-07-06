from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import openai
import PyPDF2
import io
import traceback
import os

app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', 'http://localhost:3000')}})

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
        client.models.list()
        return True
    except Exception as e:
        print(f"API Key Validation Error: {str(e)}")
        return False

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None

def generate_pitches(api_key, resume, job_description):
    client = OpenAI(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume:\n{resume}\n\nJob Description:\n{job_description}"}
            ]
        )
        content = chat_completion.choices[0].message.content
        print(content)
        pitches = []
        for i in range(1, 4):
            start = content.find(f"[PITCH{i}]") + len(f"[PITCH{i}]")
            end = content.find(f"[/PITCH{i}]")
            if start != -1 and end != -1:
                pitches.append(content[start:end].strip())
        return pitches
    except Exception as e:
        print(f"Error generating pitches: {str(e)}")
        return f"Error: {str(e)}"

# Add home route
@app.route('/')
def home():
    return "Welcome to CareerBuddy API!"

@app.route('/validate-api-key', methods=['POST'])
def api_validate_api_key():
    data = request.json
    api_key = data.get('apiKey', '')
    
    if not api_key:
        return jsonify({"error": "API key is required"}), 400

    is_valid = validate_api_key(api_key)
    return jsonify({"isValid": is_valid})

@app.route('/generate-pitches', methods=['POST'])
def api_generate_pitches():
    try:
        if request.is_json:
            data = request.json
            resume = data.get('resume', '')
            job_description = data.get('jobDescription', '')
            api_key = data.get('apiKey', '')
        else:
            data = request.form
            resume = data.get('resume', '')
            job_description = data.get('jobDescription', '')
            api_key = data.get('apiKey', '')
            if 'resumeFile' in request.files:
                pdf_file = request.files['resumeFile'].read()
                resume_text = extract_text_from_pdf(pdf_file)
                if resume_text is None:
                    return jsonify({"error": "Failed to read PDF file"}), 400
                resume = resume_text
        
        if not job_description or not api_key:
            return jsonify({"error": "Job description and API key are required"}), 400

        if not resume:
            return jsonify({"error": "Resume text or file is required"}), 400

        pitches = generate_pitches(api_key, resume, job_description)
        return jsonify({"pitches": pitches})
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)