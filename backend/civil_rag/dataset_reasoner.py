# backend/civil_rag/dataset_reasoner.py
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import os

class DatasetReasoner:
    """Reason over civil engineering datasets"""
    
    def __init__(self, dataset_path: str = "datasets"):
        self.dataset_path = dataset_path
        self.datasets = {}
        self._load_datasets()
    
    def _load_datasets(self):
        """Load all CSV datasets"""
        for file in os.listdir(self.dataset_path):
            if file.endswith('.csv'):
                name = file.replace('.csv', '')
                path = os.path.join(self.dataset_path, file)
                self.datasets[name] = pd.read_csv(path)
                print(f"📊 Loaded dataset: {name}")
    
    def analyze(self, query: str) -> pd.DataFrame:
        """Analyze dataset based on query"""
        query_lower = query.lower()
        
        # Concrete strength analysis
        if "concrete_strength" in self.datasets:
            df = self.datasets["concrete_strength"]
            
            if "high strength" in query_lower:
                return df[df["strength"] > 40].head(10)
            elif "low strength" in query_lower:
                return df[df["strength"] < 25].head(10)
            elif "average" in query_lower:
                avg = df["strength"].mean()
                return pd.DataFrame({"Metric": ["Average Strength"], "Value": [avg]})
        
        # Construction projects analysis
        if "civil_projects" in self.datasets:
            df = self.datasets["civil_projects"]
            
            if "budget" in query_lower:
                return df.nlargest(5, "budget")[["project_name", "budget"]]
        
        return pd.DataFrame({"message": ["No specific analysis found"]})
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search through datasets"""
        results = []
        query_lower = query.lower()
        
        for name, df in self.datasets.items():
            # Simple keyword matching
            for col in df.columns:
                if any(keyword in query_lower for keyword in str(col).lower().split()):
                    sample = df.head(k).to_dict('records')
                    results.extend(sample)
                    break
        
        return results[:k]

# Singleton instance
dataset_reasoner = DatasetReasoner()

def analyze_dataset(query: str):
    """Wrapper function for backward compatibility"""
    return dataset_reasoner.analyze(query)