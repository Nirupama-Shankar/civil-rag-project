"""
Agentic AI Controller - Fixed retrieval
"""

import re
from datetime import datetime

class AgenticController:
    def __init__(self, llm):
        self.llm = llm
        self.planning_history = []
    
    def plan(self, query: str):
        """Create a plan for answering"""
        steps = [{"action": "text_search", "reason": "Search documents for answer"}]
        
        # Add dataset search if query is data-related
        data_keywords = ['average', 'max', 'min', 'strength', 'data', 'calculate', 'compare']
        if any(k in query.lower() for k in data_keywords):
            steps.append({"action": "dataset_search", "reason": "Get numerical data"})
        
        # Add image search if query is image-related
        image_keywords = ['diagram', 'figure', 'image', 'show', 'display']
        if any(k in query.lower() for k in image_keywords):
            steps.append({"action": "image_search", "reason": "Find relevant images"})
        
        return {"steps": steps}
    
    def execute(self, plan, query, retrieval_func):
        """Execute the plan"""
        results = []
        for step in plan.get("steps", []):
            action = step["action"]
            print(f"⚙️ Executing: {action}")
            
            try:
                docs = retrieval_func(query, action)
                print(f"   Found {len(docs)} documents")
                
                results.append({
                    "action": action,
                    "documents": docs,
                    "count": len(docs)
                })
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "action": action,
                    "documents": [],
                    "count": 0
                })
        
        return results
    
    def reflect(self, results, plan):
        """Reflect on results"""
        total_docs = sum(r.get("count", 0) for r in results)
        return {"sufficient": total_docs > 0, "missing": "" if total_docs > 0 else "No documents found"}
    
    def answer(self, query, context, plan, results):
        """Generate answer"""
        if not context or context.strip() == "":
            return "No relevant information found in the documents. Please try rephrasing your question."
        
        try:
            response = self.llm.chat(
                model="llama3",
                messages=[{
                    "role": "user", 
                    "content": f"Answer this question based ONLY on the context:\n\nQuestion: {query}\n\nContext: {context}\n\nAnswer:"
                }]
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error: {e}"

agentic_controller = None

def init_agentic(llm):
    global agentic_controller
    agentic_controller = AgenticController(llm)
    return agentic_controller

def get_agentic():
    return agentic_controller
