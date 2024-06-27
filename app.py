from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import openai

app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = """Generate three distinct, concise, and compelling career fair pitches (each 30-60 seconds when spoken) based on the candidate's resume and the job description. Each pitch should:

1. Introduce the candidate and their relevant experience
2. Highlight key skills and achievements
3. Show alignment with the job and company
4. Invite further discussion

Ensure each pitch has a unique approach or emphasizes different aspects of the candidate's background. Label the pitches as PITCH 1, PITCH 2, and PITCH 3.

Tailor each pitch to the specific resume and job description provided, ensuring they're brief yet impactful."""

def generate_pitches(api_key, resume, job_description):
    client = OpenAI(api_key=api_key)
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Resume:\n{resume}\n\nJob Description:\n{job_description}"}
            ]
        )
        return chat_completion.choices[0].message.content
    except openai.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        return "An API error occurred. Please try again later."
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "Failed to connect to the API. Please check your internet connection and try again."
    except openai.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return "API rate limit exceeded. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred. Please try again."

@app.route('/generate-pitches', methods=['POST'])
def api_generate_pitches():
    data = request.json
    resume = data.get('resume', '')
    job_description = data.get('jobDescription', '')
    api_key = data.get('apiKey', '')
    
    if not resume or not job_description or not api_key:
        return jsonify({"error": "Resume, job description, and API key are all required"}), 400

    pitches = generate_pitches(api_key, resume, job_description)
    pitch_list = pitches.split("PITCH")
    formatted_pitches = [pitch.strip() for pitch in pitch_list if pitch.strip()]

    return jsonify({"pitches": formatted_pitches})

if __name__ == '__main__':
    app.run(debug=True)