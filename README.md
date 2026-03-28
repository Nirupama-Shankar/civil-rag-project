# Civil Engineering RAG System

A question-answering system for civil engineering documents that combines document search, data analysis, and image retrieval.

## Overview

This system allows users to upload civil engineering documents (PDFs, Word files, text files) and ask questions. The system retrieves relevant information from documents, analyzes datasets, and can find relevant diagrams or figures. It provides answers with source references.

## Features

- **Document Upload**: Upload PDF, DOCX, TXT files. The system processes and makes them searchable.
- **Text Search**: Semantic search over technical documents using vector embeddings.
- **Dataset Analysis**: Query CSV datasets (e.g., concrete strength data) for statistics like averages, maximums, and minimums.
- **Image Search**: Find and display images, diagrams, and figures extracted from documents.
- **Three Operating Modes**:
  - Standard mode for basic Q&A
  - Agentic mode that plans and executes multi-step queries
  - Multi-agent mode where specialized agents collaborate
- **Conversation Memory**: Remembers previous questions in the same session.
- **PDF Export**: Save answers as PDF files.
- **Source Attribution**: Each answer includes references to the source documents.

## Tech Stack

**Backend**
- Python, FastAPI
- FAISS for vector search
- Ollama with Llama 3 for text generation
- Sentence Transformers for text embeddings
- Neo4j for knowledge graph (concept relationships)
- CLIP for image embeddings

**Frontend**
- React
- CSS for styling
  
## Running the Project

### Backend

cd backend
pip install -r requirements.txt
python run.py

Backend will run at: http://localhost:8000

### Frontend

cd civil_ai_frontend
npm install
npm start

Frontend will run at: http://localhost:3000

### Neo4j Graph Database (Optional)

1. Install Neo4j and start the service
2. Set password in backend/civil_rag/graph_builder.py
3. Build the graph:

cd backend
python -c "from civil_rag.graph_builder import graph_builder; graph_builder.build_graph('document_name.pdf', extracted_text)"

## Usage

1. Open http://localhost:3000 in your browser
2. Select a mode (Standard, Agentic, or Multi-Agent)
3. Type your question in the input box
4. The system will retrieve relevant information and display the answer with sources
5. For image-related questions, thumbnails will appear below the answer
6. Click "Export as PDF" to save any answer

## Example Questions

- "What is concrete mix design?"
- "Show me images about concrete testing"
- "What is the average concrete strength from the dataset?"
- "What concepts are related to cement?"

## Acknowledgments

- Department of Information Technology, PSG College of Technology
