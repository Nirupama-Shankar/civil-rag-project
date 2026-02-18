import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_FOLDER = "data"

def load_document(file_path):
    extension = file_path.split(".")[-1].lower()

    if extension == "pdf":
        loader = PyPDFLoader(file_path)

    elif extension == "docx":
        loader = Docx2txtLoader(file_path)

    elif extension == "txt":
        loader = TextLoader(file_path)

    elif extension in ["md", "doc"]:
        loader = UnstructuredFileLoader(file_path)

    else:
        print(f"⚠️ Unsupported format: {file_path}")
        return []

    return loader.load()


print("📚 Starting Multi-Format Ingestion...\n")

all_documents = []

for file in os.listdir(DATA_FOLDER):
    file_path = os.path.join(DATA_FOLDER, file)

    if os.path.isfile(file_path):
        print(f"Loading {file}...")
        try:
            documents = load_document(file_path)
            print(f"   ✅ Loaded {len(documents)} sections")
            all_documents.extend(documents)
        except Exception as e:
            print(f"   ❌ Failed to load {file}: {e}")

print(f"\nTotal documents loaded: {len(all_documents)}")

# Split text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = text_splitter.split_documents(all_documents)
print(f"Total chunks created: {len(chunks)}")

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Store in FAISS
vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("vectorstore")

print("\n✅ Multi-format documents processed successfully!")
