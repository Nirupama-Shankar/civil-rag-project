"""
Multi-Agent System - Fixed version
"""

class BaseAgent:
    def __init__(self, name, llm):
        self.name = name
        self.llm = llm

class PlannerAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("Planner", llm)
    
    def think(self, query):
        steps = [{"agent": "KNOWLEDGE", "task": query}]
        
        if any(k in query.lower() for k in ['average', 'max', 'min', 'strength', 'data']):
            steps.append({"agent": "DATA", "task": query})
        if any(k in query.lower() for k in ['diagram', 'figure', 'image', 'show']):
            steps.append({"agent": "IMAGE", "task": query})
        
        return {"steps": steps, "expected_insights": "Information from documents"}

class KnowledgeAgent(BaseAgent):
    def __init__(self, llm, text_store):
        super().__init__("Knowledge", llm)
        self.text_store = text_store
    
    def think(self, task):
        if not self.text_store:
            return {"summary": "No documents available", "count": 0, "sources": []}
        
        docs = self.text_store.similarity_search(task, k=5)
        
        if not docs:
            return {"summary": "No information found", "count": 0, "sources": []}
        
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in docs]))
        summary = docs[0].page_content[:500] if docs else ""
        
        return {"summary": summary, "count": len(docs), "sources": sources, "documents": docs}

class DataAgent(BaseAgent):
    def __init__(self, llm, dataset_store):
        super().__init__("Data", llm)
        self.dataset_store = dataset_store
    
    def think(self, task):
        if not self.dataset_store:
            return {"insights": "No data available", "count": 0}
        
        docs = self.dataset_store.similarity_search(task, k=5)
        return {"insights": f"Found {len(docs)} data points", "count": len(docs)}

class ImageAgent(BaseAgent):
    def __init__(self, llm, image_store):
        super().__init__("Image", llm)
        self.image_store = image_store
    
    def think(self, task):
        if not self.image_store:
            return {"summary": "No images available", "count": 0}
        
        try:
            docs = self.image_store.similarity_search(task, k=3)
            return {"summary": f"Found {len(docs)} images", "count": len(docs)}
        except:
            return {"summary": "No images found", "count": 0}

class AnalysisAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("Analysis", llm)
    
    def think(self, inputs):
        knowledge = inputs.get("knowledge", {})
        data = inputs.get("data", {})
        
        if knowledge.get("count", 0) > 0:
            return {"analysis": knowledge.get("summary", ""), "knowledge_used": knowledge.get("count", 0)}
        return {"analysis": "No information to analyze", "knowledge_used": 0, "data_used": 0}

class ReflectionAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("Reflection", llm)
    
    def think(self, analysis, plan):
        sufficient = analysis.get("knowledge_used", 0) > 0
        return {"sufficient": sufficient, "reflection": "Analysis complete"}

class SynthesisAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("Synthesis", llm)
    
    def think(self, query, knowledge, data, images, analysis, reflection):
        if knowledge.get("count", 0) == 0:
            return "No relevant information found in the documents. Please try rephrasing your question."
        
        return knowledge.get("summary", "No information available")

class AgentOrchestrator:
    def __init__(self, llm, text_store, dataset_store, image_store):
        self.llm = llm
        self.planner = PlannerAgent(llm)
        self.knowledge = KnowledgeAgent(llm, text_store)
        self.data = DataAgent(llm, dataset_store)
        self.image = ImageAgent(llm, image_store)
        self.analysis = AnalysisAgent(llm)
        self.reflection = ReflectionAgent(llm)
        self.synthesis = SynthesisAgent(llm)
    
    def execute(self, query):
        print(f"\n🎯 MULTI-AGENT EXECUTION")
        
        # Plan
        plan = self.planner.think(query)
        
        # Execute agents
        knowledge_result = {"summary": "", "count": 0, "sources": []}
        data_result = {"insights": "", "count": 0}
        image_result = {"summary": "", "count": 0}
        
        for step in plan["steps"]:
            if step["agent"] == "KNOWLEDGE":
                knowledge_result = self.knowledge.think(step["task"])
                print(f"📚 Knowledge Agent: {knowledge_result['count']} documents")
            elif step["agent"] == "DATA":
                data_result = self.data.think(step["task"])
                print(f"📊 Data Agent: {data_result['count']} data points")
            elif step["agent"] == "IMAGE":
                image_result = self.image.think(step["task"])
                print(f"🖼️ Image Agent: {image_result['count']} images")
        
        # Analyze
        analysis_result = self.analysis.think({
            "knowledge": knowledge_result,
            "data": data_result,
            "images": image_result
        })
        
        # Reflect
        reflection_result = self.reflection.think(analysis_result, plan)
        
        # Synthesize
        final_answer = self.synthesis.think(
            query, knowledge_result, data_result, image_result,
            analysis_result, reflection_result
        )
        
        return {
            "answer": final_answer,
            "sources": knowledge_result.get("sources", []),
            "agent_metrics": {
                "knowledge_docs": knowledge_result.get("count", 0),
                "data_points": data_result.get("count", 0),
                "images_found": image_result.get("count", 0)
            }
        }

orchestrator = None

def init_orchestrator(llm, text_store, dataset_store, image_store):
    global orchestrator
    orchestrator = AgentOrchestrator(llm, text_store, dataset_store, image_store)
    return orchestrator

def get_orchestrator():
    return orchestrator
