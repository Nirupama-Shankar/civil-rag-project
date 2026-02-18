from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama

# 🔹 Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 🔹 Load FAISS vector store
vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

# 🔹 Load local LLM (Ollama)
llm = Ollama(model="llama3")

print("🚀 Civil Concrete RAG Ready! Type 'exit' to quit.\n")

while True:
    query = input("Ask a question: ")

    if query.lower() == "exit":
        print("👋 Exiting.")
        break

    # 🔍 Precise similarity-based retrieval (less noise)
    docs = vectorstore.similarity_search(query, k=4)

    if not docs:
        print("No relevant documents found.")
        continue

    # 📚 Build structured context with clear source tags
    context = ""
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        context += f"\n[Source {i+1}: {source}, Page {page}]\n"
        context += doc.page_content + "\n"

    # 🧠 Strong grounding prompt
    prompt = f"""
You are an expert in Concrete Technology.

Answer the question strictly using ONLY the provided context.

If unrelated information appears in the context,
ignore it and focus only on content directly relevant to the question.

If the answer is not clearly available, say:
"The provided documents do not contain sufficient information."

After answering, clearly mention the source number(s) used.

Context:
{context}

Question:
{query}

Answer:
"""

    # 🔹 Generate response
    response = llm.invoke(prompt)

    print("\nAnswer:\n")
    print(response)

    # 📌 Display exact PDF + page references
    print("\n📌 Source Details:")

    unique_sources = set()

    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "Unknown")
        unique_sources.add((source, page))

    for source, page in sorted(unique_sources):
        print(f"- {source} (Page {page})")


    print("-" * 60)
