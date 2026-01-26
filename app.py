from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)

llm = Ollama(model="llama3")

qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)

while True:
    query = input("Ask a question: ")
    if query.lower() == "exit":
        break
    answer = qa.run(query)
    print("\nAnswer:", answer)
