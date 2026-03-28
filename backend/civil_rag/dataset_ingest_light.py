"""
Lightweight Dataset Ingestion - Sample only
"""

import os
import pandas as pd
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

def ingest_datasets_sample(dataset_path: str = "datasets", vectorstore_path: str = "dataset_vectorstore", sample_size: int = 200):
    """
    Ingest only sample of CSV datasets to reduce processing time
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
    
    print(f"📊 Found {len(csv_files)} CSV files\n")
    
    all_documents = []
    
    for csv_file in csv_files:
        file_path = os.path.join(actual_path, csv_file)
        print(f"Processing: {csv_file}")
        
        try:
            df = pd.read_csv(file_path)
            total_rows = len(df)
            print(f"  Total rows: {total_rows}")
            
            # Take sample
            if total_rows > sample_size:
                df = df.sample(n=sample_size, random_state=42)
                print(f"  Sampling: {sample_size} rows")
            
            # Create summary statistics document
            summary = f"Dataset: {csv_file}\n"
            summary += f"Total rows in original: {total_rows}\n"
            summary += f"Columns: {', '.join(df.columns)}\n\n"
            
            # Add summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary += "Summary Statistics:\n"
                for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                    summary += f"{col} - Mean: {df[col].mean():.2f}, "
                    summary += f"Min: {df[col].min():.2f}, Max: {df[col].max():.2f}\n"
            
            # Add summary document
            all_documents.append(Document(
                page_content=summary,
                metadata={"source": csv_file, "type": "summary"}
            ))
            
            # Add sample rows as documents (limit to 50 rows)
            sample_rows = df.head(50)
            for idx, row in sample_rows.iterrows():
                row_text = f"Dataset: {csv_file}\n"
                for col in df.columns[:8]:  # Limit to first 8 columns to save space
                    row_text += f"{col}: {row[col]}\n"
                
                doc = Document(
                    page_content=row_text,
                    metadata={
                        "source": csv_file,
                        "dataset": csv_file.replace('.csv', ''),
                        "type": "sample_row"
                    }
                )
                all_documents.append(doc)
            
            print(f"  ✅ Created {len(sample_rows) + 1} documents")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if not all_documents:
        print("❌ No documents created")
        return False
    
    print(f"\n🔢 Total dataset documents: {len(all_documents)}")
    
    # Use smaller batch size for embeddings
    print("⏳ Creating embeddings (this may take a moment)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'batch_size': 32}  # Smaller batch size to reduce memory
    )
    
    # Create vectorstore with progress
    print("⏳ Building FAISS vectorstore...")
    try:
        vectorstore = FAISS.from_documents(all_documents, embeddings)
        vectorstore.save_local(vectorstore_path)
        
        print(f"\n✅ Dataset vectorstore created successfully!")
        print(f"   Location: {vectorstore_path}")
        print(f"   Total documents: {len(all_documents)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    ingest_datasets_sample()
