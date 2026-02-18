import streamlit as st
import torch
import open_clip
from PIL import Image
from spellchecker import SpellChecker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama

st.set_page_config(page_title="Civil Multimodal RAG", layout="wide")

st.title("🏗️ Civil Concrete Intelligence System")
st.write("Adaptive Multimodal RAG with Confidence & Transparency")

# -----------------------------
# SPELL CORRECTION
# -----------------------------
spell = SpellChecker()

def normalize_query(query):
    words = query.split()
    corrected_words = []
    for word in words:
        corrected = spell.correction(word)
        corrected_words.append(corrected if corrected else word)
    return " ".join(corrected_words)

# -----------------------------
# LOAD TEXT VECTORSTORE
# -----------------------------
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

text_vectorstore = load_text_vectorstore()

# -----------------------------
# LOAD IMAGE VECTORSTORE
# -----------------------------
@st.cache_resource
def load_image_vectorstore():
    return FAISS.load_local(
        "image_vectorstore",
        None,
        allow_dangerous_deserialization=True
    )

image_vectorstore = load_image_vectorstore()

# -----------------------------
# LOAD CLIP MODEL
# -----------------------------
model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='openai'
)
tokenizer = open_clip.get_tokenizer('ViT-B-32')

# -----------------------------
# LOAD LLM
# -----------------------------
llm = Ollama(model="llama3")

# -----------------------------
# USER INPUT
# -----------------------------
user_query = st.text_input("🔎 Enter your question:")

if user_query:

    # Spell correction
    normalized_query = normalize_query(user_query)

    if normalized_query != user_query:
        st.info(f"Did you mean: '{normalized_query}'?")

    query = normalized_query

    with st.spinner("Performing multimodal retrieval..."):

        # ---------------- TEXT RETRIEVAL ----------------
        text_docs_with_scores = text_vectorstore.similarity_search_with_score(query, k=4)

        text_docs = []
        text_scores = []

        for doc, score in text_docs_with_scores:
            text_docs.append(doc)
            text_scores.append(score)

        # Calibrated confidence (based on best match)
        best_text_score = min(text_scores)

        if best_text_score < 0.8:
            text_confidence = "🟢 High Confidence"
        elif best_text_score < 1.2:
            text_confidence = "🟡 Medium Confidence"
        else:
            text_confidence = "🔴 Low Confidence"

        # ---------------- IMAGE RETRIEVAL ----------------
        text_tokens = tokenizer([query])

        with torch.no_grad():
            query_embedding = model.encode_text(text_tokens)
            query_embedding = query_embedding / query_embedding.norm(dim=-1, keepdim=True)

        query_embedding = query_embedding.squeeze().tolist()

        image_docs_with_scores = image_vectorstore.similarity_search_with_score_by_vector(
            query_embedding,
            k=2
        )

        image_docs = []
        image_scores = []

        for doc, score in image_docs_with_scores:
            image_docs.append(doc)
            image_scores.append(score)

        # ---------------- BUILD TEXT CONTEXT ----------------
        context = ""
        for i, doc in enumerate(text_docs):
            source = doc.metadata.get("source", "Unknown").split("/")[-1]
            page = doc.metadata.get("page", "Unknown")
            context += f"\n[Source {i+1}: {source}, Page {page}]\n"
            context += doc.page_content + "\n"

        prompt = f"""
You are an expert in Concrete Technology.

Answer strictly using ONLY the provided text context.
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

    # ---------------- DISPLAY ANSWER ----------------
    st.subheader("📌 Answer")
    st.write(response)

    # ---------------- CONFIDENCE ----------------
    st.subheader("🔍 Text Confidence")
    st.write(text_confidence)

    # ---------------- SOURCE DETAILS ----------------
    st.subheader("📚 Text Source Details")

    unique_sources = set()
    for doc in text_docs:
        source = doc.metadata.get("source", "Unknown").split("/")[-1]
        page = doc.metadata.get("page", "Unknown")
        unique_sources.add((source, page))

    for source, page in sorted(unique_sources):
        st.write(f"- {source} (Page {page})")

    # ---------------- DISPLAY IMAGES ----------------
    st.subheader("🖼 Related Diagrams")

    for doc in image_docs:
        image_file = doc.metadata.get("source")
        image_path = f"images/{image_file}"

        try:
            image = Image.open(image_path)
            st.image(image, caption=image_file, use_column_width=True)
        except:
            st.write(f"Could not load image: {image_file}")

    # ---------------- RETRIEVAL TRANSPARENCY ----------------
    with st.expander("📖 Retrieved Text Preview"):
        for i, doc in enumerate(text_docs):
            source = doc.metadata.get("source", "Unknown").split("/")[-1]
            page = doc.metadata.get("page", "Unknown")
            st.write(f"**Source {i+1}: {source} (Page {page})**")
            st.write(doc.page_content[:400] + "...")
            st.write(f"Similarity Score: {text_scores[i]}")
            st.write("---")
