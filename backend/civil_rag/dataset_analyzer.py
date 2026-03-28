import pandas as pd
import os
import numpy as np
import re

class DatasetAnalyzer:
    def __init__(self, dataset_path="datasets"):
        possible_paths = [
            dataset_path,
            "../datasets",
            "/Users/apple/Documents/Projects/civil_rag_project/datasets",
            "/Users/apple/Documents/Projects/civil_rag_project/backend/datasets"
        ]
        
        self.datasets = {}
        
        for path in possible_paths:
            if os.path.exists(path):
                self.dataset_path = path
                print(f"✅ Found datasets at: {path}")
                self._load_datasets()
                break
        else:
            print(f"⚠️ No datasets found")
            self.dataset_path = None
    
    def _load_datasets(self):
        """Load all CSV files"""
        for file in os.listdir(self.dataset_path):
            if file.endswith('.csv'):
                name = file.replace('.csv', '')
                path = os.path.join(self.dataset_path, file)
                try:
                    df = pd.read_csv(path)
                    self.datasets[name] = df
                    print(f"📊 Loaded: {name} ({len(df)} rows, {len(df.columns)} columns)")
                except Exception as e:
                    print(f"❌ Error loading {file}: {e}")
    
    def _find_strength_column(self, df):
        """Find the strength column in the dataframe"""
        # Look for column with 'strength' or 'MPa' in name
        for col in df.columns:
            if 'strength' in col.lower() or 'mpa' in col.lower():
                return col
        # If not found, take the last numeric column (often strength)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            return numeric_cols[-1]
        return None
    
    def analyze(self, query: str) -> dict:
        """Analyze datasets based on query"""
        query_lower = query.lower()
        results = {}
        
        for name, df in self.datasets.items():
            
            if "concrete_strength" in name:
                strength_col = self._find_strength_column(df)
                
                if strength_col:
                    print(f"📊 Using strength column: {strength_col}")
                    
                    # Extract numbers from query
                    numbers = re.findall(r'\d+', query_lower)
                    threshold = int(numbers[0]) if numbers else None
                    
                    if "average" in query_lower or "mean" in query_lower:
                        avg = df[strength_col].mean()
                        results[f"average_concrete_strength"] = f"{avg:.2f} MPa"
                    
                    elif "maximum" in query_lower or "max" in query_lower or "highest" in query_lower:
                        max_val = df[strength_col].max()
                        results[f"maximum_concrete_strength"] = f"{max_val:.2f} MPa"
                    
                    elif "minimum" in query_lower or "min" in query_lower or "lowest" in query_lower:
                        min_val = df[strength_col].min()
                        results[f"minimum_concrete_strength"] = f"{min_val:.2f} MPa"
                    
                    elif "above" in query_lower or "greater than" in query_lower:
                        if threshold:
                            high_strength = df[df[strength_col] > threshold]
                            results[f"concrete_above_{threshold}_MPa"] = len(high_strength)
                            if len(high_strength) > 0:
                                results["sample_strengths"] = high_strength[strength_col].head(10).tolist()
                    
                    elif "below" in query_lower or "less than" in query_lower:
                        if threshold:
                            low_strength = df[df[strength_col] < threshold]
                            results[f"concrete_below_{threshold}_MPa"] = len(low_strength)
                    
                    elif "standard deviation" in query_lower:
                        std = df[strength_col].std()
                        results[f"standard_deviation"] = f"{std:.2f} MPa"
                    
                    elif "count" in query_lower or "how many" in query_lower:
                        results[f"total_records"] = len(df)
        
        return results
    
    def search(self, query: str, k: int = 3) -> list:
        """Search through datasets and return results as text"""
        results = self.analyze(query)
        
        if not results:
            return []
        
        text_parts = ["📊 Dataset Analysis Results:"]
        
        for key, value in results.items():
            if isinstance(value, list):
                text_parts.append(f"\n{key.replace('_', ' ').title()}:")
                for item in value[:5]:
                    text_parts.append(f"  • {item:.2f} MPa")
            elif isinstance(value, float) or isinstance(value, int):
                if 'strength' in key:
                    text_parts.append(f"• {key.replace('_', ' ').title()}: {value:.2f} MPa")
                else:
                    text_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
            else:
                text_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        return [{
            "content": "\n".join(text_parts),
            "source": "dataset_analysis",
            "metadata": {"type": "dataset"}
        }]

# Initialize
dataset_analyzer = DatasetAnalyzer()

def analyze_dataset(query: str):
    return dataset_analyzer.analyze(query)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing Dataset Analyzer")
    print("="*50)
    
    # Test queries
    test_queries = [
        "What is the average concrete strength?",
        "What is the maximum concrete strength?",
        "What is the minimum concrete strength?",
        "Show me concrete above 50 MPa"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        results = dataset_analyzer.analyze(query)
        if results:
            for key, value in results.items():
                print(f"   {key}: {value}")
        else:
            print("   No results found")
