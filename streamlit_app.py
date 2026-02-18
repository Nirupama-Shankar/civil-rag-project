import streamlit as st
import torch
import open_clip
from PIL import Image
from spellchecker import SpellChecker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
import os

st.set_page_config(
    page_title="Civil Concrete Knowledge System",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 2rem;
    max-width: 900px;
}

.stTextInput>div>div>input {
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
}

.answer-box {
    padding: 28px;
    border-radius: 14px;
    background-color: #161B22;
    border: 1px solid #2A2F36;
    margin-top: 25px;
}

.confidence-badge {
    display:inline-block;
    padding:7px 16px;
    border-radius:25px;
    color:white;
    font-size:14px;
    margin-top:20px;
    margin-bottom:30px;
}
</style>
""", unsafe_allow_html=True)

st.title("Civil Concrete Knowledge System")
st.caption("Adaptive Multimodal Retrieval with Transparency")

spell = SpellChecker()

def normalize_query(query):
    words = query.split()
    corrected_words = []
    for word in words:
        corrected = spell.correction(word)
        corrected_words.append(corrected if corrected else word)
    return " ".join(corrected_words)

@st.cache_resource
def load_text_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def load_image_vectorstore():
    return FAISS.load_local(
        "image_vectorstore",
        None,
        allow_dangerous_deserialization=True
    )

text_vectorstore = load_text_vectorstore()
image_vectorstore = load_image_vectorstore()

model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="openai"
)
tokenizer = open_clip.get_tokenizer("ViT-B-32")

llm = Ollama(model="llama3")

user_query = st.text_input("Enter your question")

if user_query:
    normalized_query = normalize_query(user_query)
    query = normalized_query

    text_docs_with_scores = text_vectorstore.similarity_search_with_score(query, k=4)

    text_docs = []
    text_scores = []

    for doc, score in text_docs_with_scores:
        text_docs.append(doc)
        text_scores.append(score)

    best_text_score = min(text_scores)

    if best_text_score < 0.8:
        text_confidence = "High Confidence"
        confidence_color = "#2E7D32"
    elif best_text_score < 1.2:
        text_confidence = "Medium Confidence"
        confidence_color = "#ED6C02"
    else:
        text_confidence = "Low Confidence"
        confidence_color = "#D32F2F"

    text_tokens = tokenizer([query])

    with torch.no_grad():
        query_embedding = model.encode_text(text_tokens)
        query_embedding = query_embedding / query_embedding.norm(dim=-1, keepdim=True)

    query_embedding = query_embedding.squeeze().tolist()

    image_docs_with_scores = image_vectorstore.similarity_search_with_score_by_vector(
        query_embedding,
        k=2
    )

    image_docs = [doc for doc, _ in image_docs_with_scores]

    context = ""
    for i, doc in enumerate(text_docs):
        source = doc.metadata.get("source", "Unknown").split("/")[-1]
        page = doc.metadata.get("page", "Unknown")
        context += f"\n[Source {i+1}: {source}, Page {page}]\n"
        context += doc.page_content + "\n"

    prompt = f"""
You are an expert in Concrete Technology.

Answer strictly using ONLY the provided context.
If the answer is not clearly available, say:
"The provided documents do not contain sufficient information."

After answering, mention source number(s) used.

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown("### Answer")
    st.write(response)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="confidence-badge" style="background:{confidence_color};">{text_confidence}</div>',
        unsafe_allow_html=True
    )

    if image_docs:
        st.markdown("### Related Diagrams")
        cols = st.columns(2)
        for i, doc in enumerate(image_docs):
            image_file = doc.metadata.get("source")
            image_path = os.path.join("images", image_file)
            try:
                image = Image.open(image_path)
                cols[i % 2].image(image, width=400)
            except:
                pass

    unique_sources = set()
    for doc in text_docs:
        source = doc.metadata.get("source", "Unknown").split("/")[-1]
        page = doc.metadata.get("page", "Unknown")
        unique_sources.add((source, page))

    with st.expander("Sources"):
        for source, page in sorted(unique_sources):
            st.write(f"{source} — Page {page}")

    with st.expander("Retrieved Context Preview"):
        for i, doc in enumerate(text_docs):
            source = doc.metadata.get("source", "Unknown").split("/")[-1]
            page = doc.metadata.get("page", "Unknown")
            st.write(f"Source {i+1}: {source} (Page {page})")
            st.write(doc.page_content[:400] + "...")
            st.write(f"Similarity Score: {text_scores[i]}")
            st.write("---")
