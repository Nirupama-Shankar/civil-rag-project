import uvicorn
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Starting Civil Engineering RAG API Server...")
    print("📁 Backend directory:", os.path.dirname(os.path.abspath(__file__)))
    print("🌐 Server will run at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        "civil_rag.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
