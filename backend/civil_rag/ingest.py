"""
Fast Document Ingestion - Instantly makes documents searchable
"""

import os
import pdfplumber
import docx2txt
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Find the backend directory
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BACKEND_DIR, "data")
VECTORSTORE_PATH = os.path.join(BACKEND_DIR, "vectorstore")

print(f"📂 Data folder: {DATA_PATH}")

# Initialize embeddings (keep in memory for speed)
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

def _extract_pdf(pdf_path: str) -> str:
    """Extract text from PDF quickly"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
        except:
            pass
    return text.strip()

def _extract_docx(docx_path: str) -> str:
    try:
        return docx2txt.process(docx_path).strip()
    except:
        return ""

def _extract_txt(txt_path: str) -> str:
    try:
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except:
        return ""

def ingest():
    """Quick ingestion - makes new documents searchable instantly"""
    
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH, exist_ok=True)
        print(f"✅ Created {DATA_PATH}")
        return
    
    all_docs = []
    supported = {".pdf", ".docx", ".txt"}
    
    # Get all files
    files_found = []
    for root, dirs, files in os.walk(DATA_PATH):
        for file in files:
            if os.path.splitext(file)[1].lower() in supported:
                files_found.append(os.path.join(root, file))
    
    if not files_found:
        return
    
    print(f"📂 Found {len(files_found)} file(s)")
    
    for file_path in files_found:
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        
        print(f"📄 Processing: {filename}")
        
        if ext == ".pdf":
            text = _extract_pdf(file_path)
        elif ext == ".docx":
            text = _extract_docx(file_path)
        elif ext == ".txt":
            text = _extract_txt(file_path)
        else:
            continue
        
        if not text or len(text.strip()) < 10:
            print(f"  ⚠️ No text extracted")
            continue
        
        chunks = SPLITTER.split_text(text)
        docs = [
            Document(
                page_content=chunk,
                metadata={"source": filename}
            )
            for chunk in chunks
        ]
        
        all_docs.extend(docs)
        print(f"  ✅ {len(chunks)} chunks")
    
    if not all_docs:
        return
    
    print(f"🔢 Total chunks: {len(all_docs)}")
    print(f"⏳ Building vectorstore...")
    
    # Create or update vectorstore
    if os.path.exists(VECTORSTORE_PATH):
        existing = FAISS.load_local(VECTORSTORE_PATH, EMBEDDINGS, allow_dangerous_deserialization=True)
        existing.add_documents(all_docs)
        existing.save_local(VECTORSTORE_PATH)
        print(f"✅ Updated! Now has {existing.index.ntotal} total chunks")
    else:
        vectorstore = FAISS.from_documents(all_docs, EMBEDDINGS)
        vectorstore.save_local(VECTORSTORE_PATH)
        print(f"✅ Created! Added {len(all_docs)} chunks")

if __name__ == "__main__":
    ingest()
