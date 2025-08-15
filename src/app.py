from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from search import hybrid_search, documents, get_document_embeddings  
from summarize import summarize_text_ollama  
from embed import get_embedding
import numpy as np

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

try:
    doc_embeddings = get_document_embeddings(documents)
except Exception as e:
    print("Error computing document embeddings:", e)
    doc_embeddings = None

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/suggest", methods=["POST"])
def suggest():
    if doc_embeddings is None:
        return jsonify({"suggestions": []})

    try:
        data = request.json
        query = data.get("query", "").strip()
        top_k = 5  

        if not query:
            return jsonify({"suggestions": []})

        query_emb = get_embedding(query)
        if query_emb.ndim == 1:
            query_emb = query_emb.reshape(1, -1)

        norms_docs = np.linalg.norm(doc_embeddings, axis=1)
        norm_query = np.linalg.norm(query_emb)
        similarities = (doc_embeddings @ query_emb.T).flatten() / (norms_docs * norm_query + 1e-8)

        top_indices = similarities.argsort()[::-1][:top_k]

        suggestions = []
        for idx in top_indices:
            doc = documents[idx]
            title = doc.get("title") if isinstance(doc, dict) else f"Document {idx+1}"
            suggestions.append(title)

        return jsonify({"suggestions": suggestions})

    except Exception as e:
        print("Suggest error:", e)
        return jsonify({"suggestions": [], "error": str(e)}), 500


@app.route("/search", methods=["POST"])
def search():
    data = request.json
    query_text = data.get("query")
    top_k = int(data.get("top_k", 5))

    if not query_text:
        return jsonify({"error": "Query is required"}), 400

    try:
        results = hybrid_search(query_text, top_k=top_k, alpha=0.5)

        print("Sending results to frontend:")
        for r in results:
            print(f"- {r['title']} | relevanceScore: {r.get('relevanceScore', 'N/A')}")

        if not results:
            return jsonify({
                "results": [],
                "message": "No relevant documents found for this query."
            })

    except Exception as e:
        print("Search error:", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"results": results})


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    docs = data.get("documents")

    if not docs or not isinstance(docs, list) or len(docs) == 0:
        return jsonify({"summary": "No relevant documents found for this query."})

    print("Documents being summarized:")
    for d in docs:
        text = d.get("text", "") if isinstance(d, dict) else str(d)
        print(text[:200], "...")

    try:
        summary = summarize_text_ollama(docs, length="medium")

        if not summary or summary.lower().strip() in ["", "no summary available"]:
            summary = "No relevant summary could be generated from the documents."
    except Exception as e:
        summary = f"Error summarizing: {str(e)}"

    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(debug=True)
