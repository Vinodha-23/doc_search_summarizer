# 🧠 LLM-Powered Document Search & Summarization with FAISS

This project is a local document search and summarization system that uses FAISS for efficient similarity search, Ollama embeddings for vectorization, and an LLM backend (via Ollama) for query understanding and summarization.

The project features a frontend interface (HTML + JavaScript) that can be hosted on GitHub Pages for easy access, while the backend runs locally.
## 🌐 Live Demo (Frontend Only)
Access the live interface here:  
**[https://vinodha-23.github.io/doc_search_summarizer/](https://vinodha-23.github.io/doc_search_summarizer/)**


------------------------------------------------------------
🚀 Features
------------------------------------------------------------
- Document Preprocessing – Preprocess raw text and store them in FAISS index.
- Semantic Search – Search across documents using embeddings and cosine similarity.
- Summarization – Summarize search results using an LLM.
- Auto-Suggestions – Get search suggestions as you type.
- Pagination – Navigate through multiple search results.
- Frontend UI – Responsive interface built with HTML, CSS, and JavaScript.
- Model Flexibility – Choose between:
  - gpt-oss – Higher quality, slower.
  - llama3.1 – Faster responses, slightly lower accuracy.
- Dataset Used – Preloaded with examples from the CNN/DailyMail dataset for summarization evaluation.

------------------------------------------------------------
📂 Project Structure
------------------------------------------------------------
project/
│── data/                  # Stores FAISS index & doc mapping
│   ├── doc_lookup.json
│── results/                # Generated and gold summaries
│── src/                    # Core backend scripts
│   ├── app.py              # Main backend API (Flask/FastAPI)
│   ├── embed.py            # Get embeddings via Ollama
│   ├── build_index.py      # Preprocess and index documents
│   ├── search.py           # Search logic
│   ├── summarize.py        # Summarization logic
│── static/                 # Static frontend assets (JS, CSS)
│── templates/              # HTML templates
│── requirements.txt        # Python dependencies
│── README.md               # Project documentation

------------------------------------------------------------
⚙️ Installation & Setup
------------------------------------------------------------
1️⃣ Clone the Repository
git clone https://github.com/your-username/document_search_llm.git
cd document_search_llm

2️⃣ Create Virtual Environment
python -m venv llm_env
source llm_env/bin/activate   # Mac/Linux
llm_env\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Install & Run Ollama
Follow the instructions from https://ollama.com/download to install Ollama on your machine.

------------------------------------------------------------
🤖 Model Selection
------------------------------------------------------------
You can run the backend with either:
- gpt-oss – More accurate but slower.
- llama3.1 – Faster but slightly less accurate.

To pull models:
ollama pull gpt-oss
ollama pull llama3.1

You can change the model in app.py config.

------------------------------------------------------------
📊 Dataset
------------------------------------------------------------
We used the CNN/DailyMail dataset for testing the summarization and search functionalities. This ensures evaluation on real-world long-form articles.

------------------------------------------------------------
▶️ Running the Backend
------------------------------------------------------------
1. Build the FAISS index (if not already built):
python src/build_index.py

2. Run the server:
python src/app.py
This will start a local API server (e.g., http://127.0.0.1:5000).

------------------------------------------------------------
💡 Example Usage
------------------------------------------------------------
1. Type a query in the search box (e.g., "What is machine learning?").
2. Auto-suggestions will appear as you type.
3. Press Enter or click search.
4. View the summarized results with pagination.
