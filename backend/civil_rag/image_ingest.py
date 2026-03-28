"""
Image Ingestion Module - Creates vectorstore for image search using CLIP
"""

import os
import torch
import open_clip
import numpy as np
from PIL import Image
import pickle
import faiss

class ImageVectorStore:
    def __init__(self):
        print("🖼️ Loading CLIP model...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            'ViT-B-32', 
            pretrained='openai'
        )
        self.model.to(self.device)
        self.model.eval()
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        print(f"✅ CLIP model loaded on {self.device}")
        
        self.embeddings = None
        self.image_paths = []
        self.image_names = []
    
    def embed_image(self, image_path):
        """Generate embedding for a single image"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
            
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
            return embedding.cpu().numpy().astype('float32').flatten()
        except Exception as e:
            print(f"❌ Error embedding {image_path}: {e}")
            return None
    
    def embed_text(self, text):
        """Generate embedding for text query"""
        text_tokens = self.tokenizer([text]).to(self.device)
        with torch.no_grad():
            embedding = self.model.encode_text(text_tokens)
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        return embedding.cpu().numpy().astype('float32').flatten()
    
    def ingest_images(self, image_folder='images', save_path='image_vectorstore'):
        """Ingest all images and save embeddings"""
        
        if not os.path.exists(image_folder):
            print(f"❌ Image folder not found: {image_folder}")
            return False
        
        # Find all images
        self.image_paths = []
        for root, dirs, files in os.walk(image_folder):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.image_paths.append(os.path.join(root, file))
                    self.image_names.append(file)
        
        if not self.image_paths:
            print(f"⚠️ No images found")
            return False
        
        print(f"📸 Found {len(self.image_paths)} images\n")
        
        # Generate embeddings
        embeddings_list = []
        for i, img_path in enumerate(self.image_paths, 1):
            print(f"Processing {i}/{len(self.image_paths)}: {os.path.basename(img_path)}")
            embedding = self.embed_image(img_path)
            if embedding is not None:
                embeddings_list.append(embedding)
            else:
                print(f"  ⚠️ Failed to embed")
        
        if not embeddings_list:
            print("❌ No images processed")
            return False
        
        self.embeddings = np.array(embeddings_list)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(self.embeddings)
        
        # Save everything
        os.makedirs(save_path, exist_ok=True)
        faiss.write_index(index, os.path.join(save_path, "index.faiss"))
        
        # Save metadata
        metadata = {
            'image_paths': self.image_paths,
            'image_names': self.image_names
        }
        with open(os.path.join(save_path, "metadata.pkl"), "wb") as f:
            pickle.dump(metadata, f)
        
        print(f"\n✅ Image vectorstore created!")
        print(f"   Total images: {len(self.image_paths)}")
        print(f"   Location: {save_path}")
        
        return True
    
    def search(self, query, k=5):
        """Search for images using text query"""
        if self.embeddings is None:
            # Load existing store
            self.load('image_vectorstore')
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        query_embedding = query_embedding.reshape(1, -1)
        
        # Load index
        index = faiss.read_index("image_vectorstore/index.faiss")
        
        # Search
        scores, indices = index.search(query_embedding, k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.image_names):
                results.append({
                    'filename': self.image_names[idx],
                    'path': self.image_paths[idx],
                    'score': float(scores[0][i])
                })
        
        return results
    
    def load(self, path='image_vectorstore'):
        """Load existing image vectorstore"""
        metadata_path = os.path.join(path, "metadata.pkl")
        if os.path.exists(metadata_path):
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            self.image_paths = metadata['image_paths']
            self.image_names = metadata['image_names']
            print(f"✅ Loaded {len(self.image_paths)} images from {path}")
            return True
        return False

# Global instance
image_store = ImageVectorStore()

def ingest_images():
    return image_store.ingest_images()

def search_images(query, k=5):
    return image_store.search(query, k)

if __name__ == "__main__":
    ingest_images()
