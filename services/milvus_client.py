from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

COLLECTION_NAME = "multimodal_rag"
DIMENSION = 768

def connect():
    connections.connect(host="localhost", port="19530")

def create_collection():
    connect()
    if utility.has_collection(COLLECTION_NAME):
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
    ]
    schema = CollectionSchema(fields=fields, description="Multimodal RAG collection")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    index_params = {
        "metric_type": "COSINE",
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 200}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    return collection

def insert_chunks(chunks: list, embeddings: list, source: str, source_type: str):
    collection = create_collection()
    data = [
        [source] * len(chunks),
        [source_type] * len(chunks),
        chunks,
        embeddings
    ]
    collection.insert(data)
    collection.flush()

def search(query_embedding: list, top_k: int = 5) -> list:
    connect()
    collection = Collection(COLLECTION_NAME)
    collection.load()

    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"ef": 100}},
        limit=top_k,
        output_fields=["chunk", "source", "source_type"]
    )

    hits = []
    for hit in results[0]:
        hits.append({
            "chunk": hit.entity.get("chunk"),
            "source": hit.entity.get("source"),
            "source_type": hit.entity.get("source_type"),
            "score": hit.score
        })
    return hits