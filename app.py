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
    from services.embedder import chunk_and_embed

@app.route("/embed", methods=["POST"])
def embed():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    chunks, embeddings = chunk_and_embed(text)
    return jsonify({"chunks": len(chunks), "embedding_dim": len(embeddings[0])})

from services.milvus_client import insert_chunks, search
from services.embedder import chunk_and_embed

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json()
    text = data.get("text", "")
    source = data.get("source", "unknown")
    source_type = data.get("source_type", "document")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    chunks, embeddings = chunk_and_embed(text)
    insert_chunks(chunks, embeddings, source, source_type)
    return jsonify({"message": "Ingested", "chunks": len(chunks)})

if __name__ == "__main__":
    app.run(debug=True)