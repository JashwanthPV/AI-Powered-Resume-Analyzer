import os
import json
import re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text

# Flask app setup
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create upload folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Check if the uploaded file is a PDF."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_resume_data(filepath):
    """Extracts text from a PDF and extracts basic info using regex instead of nltk."""
    text = extract_text(filepath)

    # Alternative to nltk: Splitting sentences using regex
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Extract basic information
    extracted_data = {
        "Name": sentences[0] if sentences else "Not Found",
        "Experience": [sent for sent in sentences if "years" in sent.lower()],
        "Skills": [sent for sent in sentences if "skills" in sent.lower()]
    }

    return extracted_data

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        if "file" not in request.files:
            return render_template("index.html", error="No file part")
        
        file = request.files["file"]
        if file.filename == "":
            return render_template("index.html", error="No selected file")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            try:
                extracted_data = extract_resume_data(filepath)

                # Save extracted data to JSON
                with open("resume_data.json", "a") as f:
                    json.dump(extracted_data, f)
                    f.write("\n")

                result = extracted_data

            except Exception as e:
                error = f"Error processing resume: {str(e)}"

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
