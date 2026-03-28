"""
Simple Image Search - Returns images based on keyword matching in filename
"""

import os
import re

class SimpleImageSearch:
    def __init__(self):
        # Get absolute path to images folder
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_folder = os.path.join(backend_dir, "images")
        self.image_paths = []
        self.image_names = []
        self.load_images()
    
    def load_images(self):
        """Load all images from folder"""
        if os.path.exists(self.image_folder):
            for root, dirs, files in os.walk(self.image_folder):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        self.image_paths.append(os.path.join(root, file))
                        self.image_names.append(file)
            print(f"📸 Loaded {len(self.image_names)} images")
        else:
            print(f"❌ Image folder not found: {self.image_folder}")
    
    def search(self, query, k=5):
        """Search images by keyword matching in filename"""
        if not self.image_names:
            return []
        
        query_lower = query.lower()
        
        # Extract keywords from query
        keywords = re.findall(r'\b\w+\b', query_lower)
        
        # Score each image based on keyword matches
        scored_images = []
        for i, name in enumerate(self.image_names):
            name_lower = name.lower()
            score = 0
            for keyword in keywords:
                if len(keyword) > 2 and keyword in name_lower:
                    score += 1
            if score > 0:
                scored_images.append((score, i))
        
        # Sort by score
        scored_images.sort(reverse=True, key=lambda x: x[0])
        
        # Return top k
        results = []
        for score, idx in scored_images[:k]:
            results.append({
                'filename': self.image_names[idx],
                'path': self.image_paths[idx],
                'score': score
            })
        
        return results

# Global instance
image_search = SimpleImageSearch()

def search_images(query, k=5):
    return image_search.search(query, k)
