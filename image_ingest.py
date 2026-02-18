import os
import torch
import open_clip
import numpy as np
from PIL import Image
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

IMAGE_FOLDER = "images"

# Load CLIP model
model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='openai'
)

image_docs = []
image_embeddings = []

for image_file in os.listdir(IMAGE_FOLDER):
    if image_file.lower().endswith((".png", ".jpg", ".jpeg")):
        image_path = os.path.join(IMAGE_FOLDER, image_file)

        image = preprocess(Image.open(image_path)).unsqueeze(0)

        with torch.no_grad():
            embedding = model.encode_image(image)

        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        embedding = embedding.squeeze().numpy().astype("float32")

        image_docs.append(
            Document(
                page_content="Extracted diagram from PDF",
                metadata={"source": image_file}
            )
        )

        image_embeddings.append(embedding)

        print(f"Embedded: {image_file}")

# Convert list to numpy array
image_embeddings = np.array(image_embeddings)

# Create FAISS index manually
dimension = image_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(image_embeddings)

# Map IDs to documents
docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(image_docs)})
index_to_docstore_id = {i: str(i) for i in range(len(image_docs))}

vectorstore = FAISS(
    embedding_function=None,
    index=index,
    docstore=docstore,
    index_to_docstore_id=index_to_docstore_id
)

vectorstore.save_local("image_vectorstore")

print("✅ Image vector store created successfully.")
