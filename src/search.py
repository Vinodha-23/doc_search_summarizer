# src/search.py
import faiss
import pickle
from embed import get_embedding  
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

INDEX_FILE = "faiss_index.index"
DOCS_FILE = "docs.pkl"

index = faiss.read_index(INDEX_FILE)
with open(DOCS_FILE, "rb") as f:
    documents = pickle.load(f) 

doc_texts = [doc["text"] if isinstance(doc, dict) else str(doc) for doc in documents]
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(doc_texts)

def get_document_embeddings(docs=None):
    """
    Returns a NumPy array of embeddings for all documents.
    If docs=None, uses the global `documents`.
    """
    docs = docs or documents
    embeddings = []
    for doc in docs:
        text = doc.get("text") if isinstance(doc, dict) else str(doc)
        emb = get_embedding(text)
        embeddings.append(emb)
    return np.vstack(embeddings)

def tfidf_search(query, top_k=5):
    query_vec = tfidf_vectorizer.transform([query])
    scores = (tfidf_matrix @ query_vec.T).toarray().flatten()
    top_indices = np.argsort(-scores)[:top_k]

    results = []
    for idx in top_indices:
        score = float(scores[idx])
        if score == 0:
            continue
        doc = documents[idx]
        if isinstance(doc, dict):
            title = doc.get("title", f"Document {idx+1}")
            text = doc.get("text", "")
        else:
            title = f"Document {idx+1}"
            text = str(doc)
        snippet = text[:200] + "..." if len(text) > 200 else text
        results.append({
            "title": title,
            "text": text,
            "snippet": snippet,
            "tfidf_score": score
        })
    return results

def search_documents(query, top_k=5):
    print(f"Running FAISS search for query: '{query}'")
    embedding = get_embedding(query)
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)
    if embedding.shape[1] != index.d:
        raise ValueError(f"Embedding dimension mismatch! Index: {index.d}, Query: {embedding.shape[1]}")

    distances, indices = index.search(embedding, top_k)
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < 0 or idx >= len(documents):
            continue
        similarity = 1 / (1 + dist)
        if similarity < SIMILARITY_THRESHOLD:
            continue
        doc = documents[idx]
        if isinstance(doc, dict):
            title = doc.get("title", f"Document {idx+1}")
            text = doc.get("text", "")
        else:
            title = f"Document {idx+1}"
            text = str(doc)
        snippet = text[:200] + "..." if len(text) > 200 else text
        results.append({
            "title": title,
            "text": text,
            "snippet": snippet,
            "distance": float(dist),
            "similarity": float(similarity)
        })
    print(f"FAISS found {len(results)} results")
    return results
SIMILARITY_THRESHOLD = 0.2 
def hybrid_search(query, top_k=10, alpha=0.5):
    """
    Perform FAISS + TF-IDF hybrid search.
    alpha: 0 = only TF-IDF, 1 = only FAISS
    """
    faiss_results = search_documents(query, top_k=top_k)
    faiss_scores = [r["similarity"] for r in faiss_results]
    if faiss_scores:
        min_f, max_f = min(faiss_scores), max(faiss_scores)
        faiss_scores = [(s - min_f) / (max_f - min_f + 1e-8) for s in faiss_scores]  # normalize 0-1
    else:
        faiss_scores = []

    tfidf_results = tfidf_search(query, top_k=top_k)
    tfidf_scores = [r["tfidf_score"] for r in tfidf_results]
    if tfidf_scores:
        min_t, max_t = min(tfidf_scores), max(tfidf_scores)
        tfidf_scores = [(s - min_t) / (max_t - min_t + 1e-8) for s in tfidf_scores]  # normalize 0-1
    else:
        tfidf_scores = []

    merged_results = {}

    for i, r in enumerate(faiss_results):
        title = r["title"]
        text = r["text"]
        tfidf_score = 0
        for t, t_r in enumerate(tfidf_results):
            if t_r["title"] == title:
                tfidf_score = tfidf_scores[t]
                break
        relevanceScore = alpha * faiss_scores[i] + (1 - alpha) * tfidf_score
        merged_results[title] = {
            "title": title,
            "text": text,
            "snippet": text[:200] + "..." if len(text) > 200 else text,
            "relevanceScore": round(float(relevanceScore), 2)
        }

    for i, r in enumerate(tfidf_results):
        title = r["title"]
        if title not in merged_results:
            merged_results[title] = {
                "title": title,
                "text": r["text"],
                "snippet": r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"],
                "relevanceScore": round(tfidf_scores[i] * (1 - alpha), 2)
            }

    results_list = sorted(merged_results.values(), key=lambda x: x["relevanceScore"], reverse=True)

    return results_list[:max(top_k, len(results_list))]

