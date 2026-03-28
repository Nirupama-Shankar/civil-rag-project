"""
Hybrid Retriever - Searches ALL text documents regardless of topic
"""

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from .dataset_analyzer import dataset_analyzer
import numpy as np

VALID_TOOLS = {"text_search", "dataset_search", "image_search", "ocr_search"}

def _normalize(scores: list[float]) -> list[float]:
    """Min-max normalize scores"""
    if not scores:
        return []
    mn, mx = min(scores), max(scores)
    if mx == mn:
        return [1.0] * len(scores)
    return [(s - mn) / (mx - mn) for s in scores]

def _bm25_rerank(query: str, docs: list[Document]) -> list[tuple[float, Document]]:
    """Re-rank documents using BM25"""
    if not docs:
        return []
    tokenized = [doc.page_content.lower().split() for doc in docs]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.lower().split())
    return list(zip(scores, docs))

def hybrid_retrieval(
    query: str,
    text_store,
    dataset_store,
    image_store,
    tools: list[str],
    top_k: int = 5
) -> list[Document]:
    """
    Hybrid retrieval - searches ALL text documents regardless of topic
    """
    # Validate tools
    tools = [t for t in tools if t in VALID_TOOLS]
    if not tools:
        tools = ["text_search"]
    
    raw_docs = []
    
    # 1. TEXT SEARCH - ALWAYS search text_store for ANY text query
    # This is the key fix - it should search ALL text documents
    if "text_search" in tools and text_store:
        print(f"🔍 Searching ALL text documents...")
        text_docs = text_store.similarity_search(query, k=10)
        raw_docs.extend(text_docs)
        print(f"   Found {len(text_docs)} text documents")
    
    # 2. DATASET SEARCH - for CSV data
    if "dataset_search" in tools:
        print(f"📊 Analyzing datasets...")
        analysis_results = dataset_analyzer.search(query)
        if analysis_results:
            for result in analysis_results:
                doc = Document(
                    page_content=result["content"],
                    metadata={
                        "source": result["source"],
                        "type": "dataset_analysis"
                    }
                )
                raw_docs.append(doc)
            print(f"   Found {len(analysis_results)} dataset insights")
    
    # 3. IMAGE SEARCH - for images
    if "image_search" in tools and image_store:
        print(f"��️ Searching images...")
        try:
            image_docs = image_store.similarity_search(query, k=5)
            raw_docs.extend(image_docs)
            print(f"   Found {len(image_docs)} relevant images")
        except Exception as e:
            print(f"   ⚠️ Image search error: {e}")
    
    if not raw_docs:
        print("⚠️ No documents retrieved")
        return []
    
    # Remove duplicates by content
    seen = set()
    unique_docs = []
    for doc in raw_docs:
        key = doc.page_content[:120]
        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)
    
    # Re-rank with BM25
    scored = _bm25_rerank(query, unique_docs)
    bm25_scores = [s for s, _ in scored]
    norm_scores = _normalize(bm25_scores)
    
    ranked = sorted(
        zip(norm_scores, [doc for _, doc in scored]),
        key=lambda x: x[0],
        reverse=True
    )
    
    final_docs = [doc for _, doc in ranked[:top_k]]
    print(f"✅ Returning {len(final_docs)} documents after re-ranking")
    
    return final_docs

def search_images(query: str, image_store, k: int = 5):
    """Search for images and return them"""
    if not image_store:
        return []
    
    results = image_store.similarity_search(query, k=k)
    
    images = []
    for doc in results:
        images.append({
            "filename": doc.metadata.get("source", ""),
            "description": doc.page_content,
            "path": doc.metadata.get("path", "")
        })
    
    return images

def graph_augmented_retrieval(query: str, text_store, graph_builder, top_k: int = 5) -> list[Document]:
    """Enhanced retrieval with graph context"""
    
    # Get graph context
    graph_context = graph_builder.get_graph_context(query)
    
    # Augment query with graph context
    augmented_query = f"{query}\n\nRelated concepts: {graph_context}"
    
    # Perform vector search with augmented query
    docs = text_store.similarity_search(augmented_query, k=top_k)
    
    return docs
