from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


from services.transcriber import transcribe_audio

@app.route("/transcribe", methods=["POST"])
def transcribe():
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    transcript = transcribe_audio(path)
    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(debug=True)