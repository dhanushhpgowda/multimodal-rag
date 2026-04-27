# Multimodal RAG — Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [Environment Setup](#environment-setup)
5. [Services](#services)
6. [API Reference](#api-reference)
7. [Vector Database](#vector-database)
8. [UI Guide](#ui-guide)
9. [How RAG Works](#how-rag-works)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

Multimodal RAG is a Retrieval-Augmented Generation pipeline that accepts both audio files and text documents as input. It transcribes, chunks, embeds, and stores content in a vector database, then answers user questions grounded in the uploaded data.

Built as a 7-day public portfolio project using open-source tools and free-tier APIs.

---

## Architecture

```
User Upload (Audio / Document)
        │
        ▼
┌───────────────────┐
│   Flask Web App   │
└───────────────────┘
        │
        ├── Audio → Whisper (Groq API) → Transcript
        │
        └── Document → Raw Text
                │
                ▼
        ┌───────────────┐
        │  Text Chunker  │
        └───────────────┘
                │
                ▼
        ┌───────────────┐
        │   Embedder    │  ← paraphrase-multilingual-mpnet-base-v2
        └───────────────┘
                │
                ▼
        ┌───────────────┐
        │    Milvus     │  ← HNSW Index, Cosine Similarity
        └───────────────┘

User Question
        │
        ▼
┌───────────────────┐
│  Query Embedding  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Milvus Search    │  ← Top 5 relevant chunks
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Llama 3.3 70B    │  ← Groq API
└───────────────────┘
        │
        ▼
   Answer + Sources
```

---

## Folder Structure

```
multimodal-rag/
├── app.py                   # Flask app, all routes
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Milvus + Attu + MinIO + etcd
├── .env                     # API keys (not committed)
├── .gitignore
├── templates/
│   └── index.html           # Full dark mode UI
├── services/
│   ├── transcriber.py       # Whisper transcription via Groq
│   ├── embedder.py          # Text chunking + embedding
│   ├── milvus_client.py     # Milvus insert + search
│   └── rag.py               # RAG pipeline + LLM call
└── uploads/                 # Uploaded files (not committed)
```

---

## Environment Setup

### Requirements

- Python 3.9+
- Docker Desktop
- Groq API key (free at https://console.groq.com)

### Steps

```bash
# 1. Clone
git clone https://github.com/dhanushhpgowda/multimodal-rag.git
cd multimodal-rag

# 2. Create .env
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Start vector database
docker-compose up -d

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run app
python app.py
```

App runs at: http://localhost:5000
Attu UI runs at: http://localhost:8000

---

## Services

### services/transcriber.py

Handles audio transcription using Whisper large-v3-turbo via the Groq API.

| Function | Input | Output |
|---|---|---|
| transcribe_audio(file_path) | Path to audio file | Transcript string |

Supported formats: .mp3, .wav, .m4a, .ogg, .flac

---

### services/embedder.py

Handles text chunking and embedding using sentence-transformers.

| Function | Input | Output |
|---|---|---|
| chunk_text(text, chunk_size, overlap) | Raw text string | List of text chunks |
| embed_chunks(chunks) | List of strings | List of float vectors |
| chunk_and_embed(text) | Raw text string | Tuple (chunks, embeddings) |

Model: paraphrase-multilingual-mpnet-base-v2
Embedding dimension: 768
Chunk size: 300 words
Overlap: 50 words

---

### services/milvus_client.py

Handles all Milvus vector database operations.

| Function | Input | Output |
|---|---|---|
| connect() | — | Opens Milvus connection |
| create_collection() | — | Creates or returns collection |
| insert_chunks(chunks, embeddings, source, source_type) | Lists + metadata | Inserts into Milvus |
| search(query_embedding, top_k) | Vector + int | List of top matches |

Collection name: multimodal_rag
Index type: HNSW
Metric: Cosine similarity
Schema fields: id, source, source_type, chunk, embedding

---

### services/rag.py

Orchestrates the full RAG pipeline.

| Function | Input | Output |
|---|---|---|
| answer_question(query) | Question string | Dict with answer + sources |

Flow:
1. Embeds the user query
2. Searches Milvus for top 5 relevant chunks
3. Builds a grounded prompt with retrieved context
4. Calls Llama 3.3 70B via Groq
5. Returns answer + source citations

---

## API Reference

### GET /health

Health check endpoint.

Response:
{ "status": "ok" }

---

### POST /upload

Upload and index an audio file or document.

Request: multipart/form-data

| Field | Type | Description |
|---|---|---|
| file | File | Audio or text file |

Response:
{
  "message": "Processed filename.mp3",
  "chunks": 12,
  "source_type": "audio"
}

Supported types:
- Audio: .mp3, .wav, .m4a, .ogg, .flac
- Document: .txt

---

### POST /transcribe

Transcribe an audio file only (no indexing).

Request: multipart/form-data

| Field | Type | Description |
|---|---|---|
| audio | File | Audio file |

Response:
{ "transcript": "Hello this is the transcribed text..." }

---

### POST /embed

Chunk and embed a raw text string (no indexing).

Request: application/json
{ "text": "Your text here" }

Response:
{ "chunks": 3, "embedding_dim": 768 }

---

### POST /ingest

Manually ingest raw text into Milvus.

Request: application/json
{
  "text": "Your text here",
  "source": "myfile.txt",
  "source_type": "document"
}

Response:
{ "message": "Ingested", "chunks": 5 }

---

### POST /ask

Ask a question grounded in indexed data.

Request: application/json
{ "query": "What was discussed in the meeting?" }

Response:
{
  "answer": "The meeting covered quarterly targets and...",
  "sources": [
    { "source": "meeting.mp3", "type": "audio", "score": 0.91 },
    { "source": "notes.txt", "type": "document", "score": 0.87 }
  ]
}

---

## Vector Database

### Milvus Collection Schema

| Field | Type | Details |
|---|---|---|
| id | INT64 | Primary key, auto-generated |
| source | VARCHAR(200) | Original filename |
| source_type | VARCHAR(50) | audio or document |
| chunk | VARCHAR(2000) | Text chunk content |
| embedding | FLOAT_VECTOR(768) | Dense embedding vector |

### Index Configuration

Index type:     HNSW
Metric type:    COSINE
M:              16
efConstruction: 200
ef (search):    100

### Attu UI

Access Milvus visually at http://localhost:8000
Connect with: milvus:19530

---

## UI Guide

The frontend is a single templates/index.html file with no external frameworks.

### Left Panel — Knowledge Base

- Drag and drop or click to select a file
- Click Upload to process and index the file
- Indexed files appear in the list with chunk count
- Audio files shown with mic icon, documents with doc icon

### Right Panel — Chat

- Type a question and press Enter to send
- Use Shift+Enter for a new line
- Answers appear with source citations below
- Sources show filename, type, and similarity score

---

## How RAG Works

RAG = Retrieval-Augmented Generation

Instead of asking an LLM to answer from its training data, RAG first retrieves relevant content from your own uploaded files, then passes that content as context to the LLM.

Step by step:

1. User uploads a file → chunked into ~300 word segments
2. Each chunk is converted to a 768-dimensional vector
3. Vectors stored in Milvus with metadata
4. User asks a question → question is also embedded
5. Milvus finds the top 5 most similar chunks by cosine similarity
6. Those chunks are passed to Llama 3.3 70B as context
7. LLM answers only using that context → grounded, accurate response

Multimodal means both audio transcripts and text documents are stored together in the same vector space and retrieved together in a single search.

---

## Troubleshooting

### Milvus container conflict

```bash
docker-compose down
docker stop milvus-minio milvus-etcd milvus-standalone
docker rm milvus-minio milvus-etcd milvus-standalone
docker-compose up -d
```

### version warning in docker-compose

Remove the version: line from docker-compose.yml. It is obsolete in newer Docker versions.

### PowerShell && not working

Run commands separately:
docker-compose down
docker-compose up -d

### Embedding model slow on first run

The sentence-transformer model downloads on first use (~420MB). Subsequent runs load from cache.

### Groq rate limit

Groq free tier has rate limits. If you hit them, wait 60 seconds and retry.

### Port already in use

| Service | Port | Fix |
|---|---|---|
| Flask | 5000 | python app.py --port 5001 |
| Milvus | 19530 | Stop conflicting container |
| Attu | 8000 | Change in docker-compose.yml |
| MinIO | 9000 | Change in docker-compose.yml |