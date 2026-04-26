import os
from groq import Groq
from services.embedder import chunk_and_embed, embed_chunks
from services.milvus_client import search

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def answer_question(query: str) -> dict:
    _, query_embedding = chunk_and_embed(query)
    query_vec = query_embedding[0]

    results = search(query_vec, top_k=5)

    if not results:
        return {"answer": "No relevant context found. Please upload some files first.", "sources": []}

    context = "\n\n".join([
        f"[Source: {r['source']} | Type: {r['source_type']}]\n{r['chunk']}"
        for r in results
    ])

    prompt = f"""You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information."

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    answer = response.choices[0].message.content

    sources = [{"source": r["source"], "type": r["source_type"], "score": round(r["score"], 3)} for r in results]

    return {"answer": answer, "sources": sources}