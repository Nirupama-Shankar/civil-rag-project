from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import ollama
import os

from .hybrid_retriever import hybrid_retrieval
from .agent_controller import agent_plan
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = FastAPI(title="Civil Engineering RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def load_vectorstore(path: str):
    possible_paths = [
        path,
        f"../{path}",
        f"/Users/apple/Documents/Projects/civil_rag_project/backend/{path}",
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            print(f"✅ Found vectorstore at: {p}")
            try:
                return FAISS.load_local(
                    p, embeddings, allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"⚠️ Error loading {p}: {e}")
    print(f"⚠️ Vectorstore not found: {path}")
    return None

text_store = load_vectorstore("vectorstore")
dataset_store = load_vectorstore("dataset_vectorstore")
image_store = load_vectorstore("image_vectorstore")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    tools: List[str]
    sources: List[str]

@app.get("/")
def root():
    return {
        "name": "Civil Engineering RAG System",
        "version": "1.0.0",
        "status": "running",
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
# Add to api.py
@app.get("/graph/{concept}")
async def get_concept_graph(concept: str):
    """Get graph visualization data for a concept"""
    from .graph_builder import graph_builder
    
    relations = graph_builder.query_relationships(concept, depth=2)
    
    # Format for visualization
    nodes = [{"id": concept, "group": 1}]
    links = []
    
    for rel in relations['related']:
        nodes.append({"id": rel['concept'], "group": 2})
        links.append({
            "source": concept,
            "target": rel['concept'],
            "distance": rel['distance']
        })
    
    return {"nodes": nodes, "links": links}
@app.post("/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    print(f"\n📝 Question: {req.query}")
    
    tools = agent_plan(req.query, ollama)
    print(f"��️ Tools selected: {tools}")
    
    docs = hybrid_retrieval(
        req.query,
        text_store,
        dataset_store,
        image_store,
        tools
    )
    
    if not docs:
        print("⚠️ No documents retrieved")
        return QueryResponse(
            answer="No relevant information found in the documents.",
            tools=tools,
            sources=[]
        )
    
    print(f"📄 Retrieved {len(docs)} documents")
    
    # Print first 3 documents for debugging
    print("\n" + "="*50)
    print("RETRIEVED DOCUMENTS:")
    print("="*50)
    for i, doc in enumerate(docs[:3]):
        print(f"\n--- Document {i+1} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content: {doc.page_content[:300]}...")
    print("="*50 + "\n")
    
    # Build context with clear source markers
    context_parts = []
    for doc in docs[:5]:
        source = doc.metadata.get('source', 'Unknown')
        context_parts.append(f"[SOURCE: {source}]\n{doc.page_content}")
    
    context = "\n\n".join(context_parts)
    
    # Enhanced prompt with clearer instructions
    prompt = f"""You are a civil engineering expert. Answer the question based ONLY on the provided context.

CONTEXT:
{context}

QUESTION: {req.query}

INSTRUCTIONS:
1. Answer using ONLY the information in the context above
2. If the context contains the answer, provide it directly
3. If the context does NOT contain the answer, say "The information is not available in the provided documents"
4. Be specific and cite the source when possible

ANSWER:"""
    
    print(f"📝 Prompt length: {len(prompt)} characters")
    print(f"📝 Context length: {len(context)} characters")
    
    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
        print(f"✅ Generated answer: {answer[:100]}...")
    except Exception as e:
        print(f"❌ LLM error: {e}")
        answer = f"Error: {str(e)}"
    
    sources = list({doc.metadata.get("source", "Unknown") for doc in docs[:5]})
    
    return QueryResponse(
        answer=answer,
        tools=tools,
        sources=sources
    )
