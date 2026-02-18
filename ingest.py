import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = "data"

all_documents = []

print("📚 Starting PDF ingestion...\n")

# 🔹 Load all PDFs safely
for file in os.listdir(DATA_PATH):
    if file.endswith(".pdf"):
        file_path = os.path.join(DATA_PATH, file)
        print(f"Loading {file}...")

        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            all_documents.extend(documents)
            print(f"   ✅ Loaded {len(documents)} pages")

        except Exception as e:
            print(f"   ⚠️ Skipping {file} due to error:")
            print(f"      {e}\n")

print(f"\nTotal pages successfully loaded: {len(all_documents)}")

if len(all_documents) == 0:
    print("❌ No documents loaded. Exiting.")
    exit()

# 🔹 Strong chunking strategy
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=120

)

chunks = text_splitter.split_documents(all_documents)

print(f"Total chunks created: {len(chunks)}")

# 🔹 Create embeddings
print("\n🧠 Generating embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 🔹 Create FAISS index
print("🗂️ Building vector store...")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 🔹 Save vectorstore
vectorstore.save_local("vectorstore")

print("\n✅ All valid PDFs processed and stored in vector DB successfully!")
