"""
Dataset Ingestion Module
Creates vectorstore from CSV files for semantic search
"""

import os
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def ingest_datasets(dataset_path: str = "datasets", vectorstore_path: str = "dataset_vectorstore"):
    """
    Ingest all CSV datasets into FAISS vectorstore
    """
    # Find correct dataset path
    possible_paths = [
        dataset_path,
        "../datasets",
        "/Users/apple/Documents/Projects/civil_rag_project/datasets",
        "/Users/apple/Documents/Projects/civil_rag_project/backend/datasets"
    ]
    
    actual_path = None
    for path in possible_paths:
        if os.path.exists(path):
            actual_path = path
            break
    
    if not actual_path:
        print(f"❌ Dataset folder not found")
        return False
    
    print(f"📂 Found datasets at: {actual_path}")
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(actual_path) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"❌ No CSV files found")
        return False
    
    print(f"📊 Found {len(csv_files)} CSV files to ingest\n")
    
    all_documents = []
    
    for csv_file in csv_files:
        file_path = os.path.join(actual_path, csv_file)
        print(f"Processing: {csv_file}")
        
        try:
            df = pd.read_csv(file_path)
            print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")
            
            # Convert each row to a document
            for idx, row in df.iterrows():
                # Create text representation of the row
                row_text = f"Dataset: {csv_file}\n"
                for col in df.columns:
                    row_text += f"{col}: {row[col]}\n"
                
                doc = Document(
                    page_content=row_text,
                    metadata={
                        "source": csv_file,
                        "row_index": idx,
                        "dataset": csv_file.replace('.csv', '')
                    }
                )
                all_documents.append(doc)
            
            print(f"  ✅ Created {len(df)} documents")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if not all_documents:
        print("❌ No documents created")
        return False
    
    print(f"\n🔢 Total dataset documents: {len(all_documents)}")
    
    # Create embeddings
    print("⏳ Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create vectorstore
    print("⏳ Building FAISS vectorstore...")
    vectorstore = FAISS.from_documents(all_documents, embeddings)
    
    # Save
    vectorstore.save_local(vectorstore_path)
    
    print(f"\n✅ Dataset vectorstore created successfully!")
    print(f"   Location: {vectorstore_path}")
    print(f"   Total documents: {len(all_documents)}")
    
    return True

if __name__ == "__main__":
    ingest_datasets()
