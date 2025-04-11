from flask import Flask, request, render_template, send_file
from gtts import gTTS
import os
import fitz  # PyMuPDF for PDF text extraction

app = Flask(__name__)
UPLOAD_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded"

    file = request.files['file']
    if file.filename == '':
        return "No file selected"
    
    # Ensure the file is a PDF
    if not file.filename.endswith('.pdf'):
        return "Only PDF files are allowed"

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from PDF
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return "No text found in the PDF"

    # Convert text to speech
    tts = gTTS(text)
    audio_path = os.path.join(UPLOAD_FOLDER, 'output.mp3')
    tts.save(audio_path)

    return render_template('index.html', audio_file='static/audio/output.mp3')

@app.route('/download')
def download_audio():
    return send_file("static/audio/output.mp3", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
