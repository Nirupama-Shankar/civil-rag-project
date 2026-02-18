Built as an exploration of multimodal retrieval and grounded LLM reasoning in domain-specific technical documents.
**Civil Multimodal RAG System**

A multimodal Retrieval-Augmented Generation (RAG) system for Civil Engineering documents.
This project enables users to ask questions from technical PDF books (Concrete Technology, Civil Materials, etc.) and receive grounded answers with proper page citations and related diagrams.

🚀 Key Features

Semantic search over engineering PDFs using FAISS
Automatic diagram extraction from documents
CLIP-based image retrieval alongside text answers
Confidence scoring for transparency
Source citation with exact page numbers
Streamlit-based interactive UI

🧠 Tech Stack

Python
FAISS (vector database)
Sentence Transformers (text embeddings)
OpenCLIP (image embeddings)
Ollama (LLM inference)
Streamlit (frontend)

▶ Run Locally

pip install -r requirements.txt
python extract_images.py
python ingest.py
python image_ingest.py
streamlit run streamlit_app.py

📌 Project Focus
Built to explore practical multimodal RAG systems combining text + diagram retrieval for domain-specific question answering in Civil Engineering.
