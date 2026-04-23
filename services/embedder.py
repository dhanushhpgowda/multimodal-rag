from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def embed_chunks(chunks: list) -> list:
    embeddings = model.encode(chunks, show_progress_bar=False)
    return embeddings.tolist()

def chunk_and_embed(text: str) -> tuple:
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    return chunks, embeddings