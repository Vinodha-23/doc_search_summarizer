# src/build_index.py
import pickle
import faiss
import numpy as np
from embed import get_embedding  

DOCS_FILE = "docs.pkl"
INDEX_FILE = "faiss_index.index"

with open(DOCS_FILE, "rb") as f:
    documents = pickle.load(f)  

print(f"Loaded {len(documents)} documents.")

print("Generating embeddings...")
embeddings = np.array([get_embedding(doc['text']).flatten() for doc in documents], dtype="float32")
print(f"Embeddings shape: {embeddings.shape}")

dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  
print(f"Creating FAISS index with dimension {dim}...")

index.add(embeddings)
print(f"FAISS index contains {index.ntotal} vectors.")

faiss.write_index(index, INDEX_FILE)
print(f"Saved FAISS index to {INDEX_FILE}.")

DOC_LOOKUP_FILE = "docs.pkl"  
with open(DOC_LOOKUP_FILE, "wb") as f:
    pickle.dump(documents, f)
print(f"Documents saved to {DOC_LOOKUP_FILE}.")
