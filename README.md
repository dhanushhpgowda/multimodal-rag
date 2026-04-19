# Multimodal RAG — Audio + Documents

A portfolio project that combines audio transcription and document parsing into a unified Retrieval-Augmented Generation (RAG) pipeline.

## What it does
- Accepts audio files and documents (PDF, TXT) as input
- Transcribes audio using Whisper large-v3-turbo
- Chunks and embeds content using paraphrase-multilingual-mpnet-base-v2
- Stores embeddings in Milvus vector database
- Retrieves relevant context across both audio and document sources
- Answers questions grounded in the uploaded data using Llama 3.3 70B

## Stack
| Layer | Tool |
|---|---|
| Web app | Flask |
| Vector DB | Milvus (Docker) |
| DB UI | Attu |
| LLM | Llama 3.3 70B (IBM watsonx) |
| Embeddings | sentence-transformers/paraphrase-multilingual-mpnet-base-v2 |
| Transcription | openai/whisper-large-v3-turbo |

## Project Structure (building day by day)


## Status
🔨 Work in progress — built in public over 7 days.