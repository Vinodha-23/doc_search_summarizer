# src/embed.py
import json
import numpy as np
import faiss
from ollama import embeddings  # Ollama embeddings API

MODEL_NAME = "nomic-embed-text"

def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding for a single string.
    Returns 2D array with shape (1, 1536)
    """
    response = embeddings(model=MODEL_NAME, prompt=text)
    emb = np.array(response.embedding, dtype=np.float32)
    return emb.reshape(1, -1)

def build_faiss_index(docs, index_path="models/index.faiss", mapping_path="data/doc_lookup.json"):
    """
    Build and save FAISS index + document lookup from a list of docs.
    """
    print("Generating embeddings...")
    embeddings_list = [get_embedding(doc) for doc in docs]
    embeddings_np = np.vstack(embeddings_list)

    print(f"Creating FAISS index with dim={embeddings_np.shape[1]}")
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)

    print(f"Saving FAISS index to {index_path}")
    faiss.write_index(index, index_path)

    print(f"Saving doc lookup to {mapping_path}")
    doc_map = {str(i): doc for i, doc in enumerate(docs)}
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(doc_map, f)

    print("✅ FAISS index and document mapping saved successfully!")

# Example usage:
if __name__ == "__main__":
    sample_docs = [
        "Document 1 content here.",
        "Document 2 content here.",
        "Document 3 content here."
    ]
    build_faiss_index(sample_docs)
