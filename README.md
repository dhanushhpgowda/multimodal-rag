# Multimodal RAG — Audio + Documents

A portfolio project that combines audio transcription and document parsing into a unified Retrieval-Augmented Generation (RAG) pipeline. Ask questions grounded in your uploaded audio and documents.

---

## What it does

- Upload audio files (mp3, wav, m4a) and documents (txt)
- Transcribes audio using Whisper large-v3-turbo via Groq API
- Chunks and embeds content using paraphrase-multilingual-mpnet-base-v2
- Stores embeddings in Milvus vector database with HNSW indexing
- Retrieves relevant context using cosine similarity search
- Answers questions using Llama 3.3 70B via Groq API
- Clean dark mode UI with source citations per answer

---

## Stack

| Layer | Tool |
|---|---|
| Web app | Flask |
| Vector DB | Milvus (Docker) |
| DB UI | Attu |
| LLM | Llama 3.3 70B (Groq) |
| Embeddings | sentence-transformers/paraphrase-multilingual-mpnet-base-v2 |
| Transcription | openai/whisper-large-v3-turbo (Groq) |

---

## Project Structure