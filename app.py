from flask import Flask, request, render_template, send_file, url_for
from gtts import gTTS
import os
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
from PIL import Image

# For Windows (Modify the path if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


app = Flask(__name__)

# Folders
UPLOAD_FOLDER = "uploads"
AUDIO_FOLDER = "static/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Function to extract text
def extract_text(file_path, file_type):
    text = ""
    if file_type == 'pdf':
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    elif file_type == 'txt':
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif file_type in ['jpg', 'jpeg', 'png']:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
    return text.strip()

@app.route('/')
def index():
    return render_template('index.html', audio_file=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded"
    
    file = request.files['file']
    if file.filename == '':
        return "No file selected"

    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ['pdf', 'txt', 'jpg', 'jpeg', 'png']:
        return "Unsupported file format. Please upload a PDF, Text, or Image file."
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    text = extract_text(file_path, file_extension)

    if not text:
        return "No text found in the file."

    audio_path = os.path.join(AUDIO_FOLDER, 'output.mp3')
    tts = gTTS(text)
    tts.save(audio_path)

    return render_template('index.html', audio_file=url_for('static', filename='audio/output.mp3'))

@app.route('/download')
def download_audio():
    audio_path = os.path.join(AUDIO_FOLDER, 'output.mp3')
    return send_file(audio_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
