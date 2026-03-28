"""
Graph Builder for Civil Engineering Knowledge
"""

from neo4j import GraphDatabase
from typing import List, Dict

class GraphBuilder:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="Niru_1746"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"✅ Connected to Neo4j at {uri}")
    
    def close(self):
        self.driver.close()
    
    def extract_concepts(self, text: str) -> List[str]:
        concepts = {
            'cement', 'concrete', 'aggregate', 'sand', 'water', 
            'admixture', 'fly ash', 'slag', 'strength', 'durability', 
            'workability', 'permeability', 'shrinkage',
            'm20', 'm25', 'm30', 'slump test', 
            'compressive strength', 'tensile strength',
            'is 456', 'astm c39', 'water-cement ratio', 'w/c ratio',
            'curing', 'compaction', 'hydration', 'opc', 'ppc'
        }
        
        found = []
        text_lower = text.lower()
        for concept in concepts:
            if concept in text_lower:
                found.append(concept)
        return found
    
    def build_graph(self, document_name: str, text: str):
        concepts = self.extract_concepts(text)
        
        if not concepts:
            print(f"⚠️ No concepts found in {document_name}")
            return
        
        with self.driver.session() as session:
            session.run("MERGE (d:Document {name: $name})", name=document_name)
            
            for concept in concepts:
                session.run("""
                    MERGE (c:Concept {name: $concept})
                    MERGE (d:Document {name: $doc_name})
                    MERGE (d)-[:CONTAINS]->(c)
                """, concept=concept, doc_name=document_name)
            
            for i, c1 in enumerate(concepts):
                for c2 in concepts[i+1:]:
                    session.run("""
                        MATCH (c1:Concept {name: $c1})
                        MATCH (c2:Concept {name: $c2})
                        MERGE (c1)-[:RELATED_TO]-(c2)
                    """, c1=c1, c2=c2)
        
        print(f"✅ Built graph for {document_name}: {len(concepts)} concepts")
    
    def get_all_concepts(self) -> List[str]:
        with self.driver.session() as session:
            result = session.run("MATCH (c:Concept) RETURN c.name as name ORDER BY name")
            return [record["name"] for record in result]
    
    def query_relationships(self, concept: str, depth: int = 2) -> Dict:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $concept})
                MATCH (c)-[:RELATED_TO]-(related)
                RETURN DISTINCT related.name as concept
                LIMIT 20
            """, concept=concept.lower())
            
            relationships = []
            for record in result:
                relationships.append({"concept": record["concept"], "distance": 1})
            
            return {"concept": concept, "related": relationships}
    
    def get_documents_for_concept(self, concept: str) -> List[str]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)-[:CONTAINS]->(c:Concept {name: $concept})
                RETURN d.name as document
            """, concept=concept.lower())
            return [record["document"] for record in result]

graph_builder = GraphBuilder()

def get_all_concepts():
    return graph_builder.get_all_concepts()

def query_relationships(concept: str, depth: int = 2):
    return graph_builder.query_relationships(concept, depth)

def get_documents_for_concept(concept: str):
    return graph_builder.get_documents_for_concept(concept)

if __name__ == "__main__":
    try:
        concepts = get_all_concepts()
        print(f"Found {len(concepts)} concepts")
        print(f"Sample: {concepts[:10]}")
    except Exception as e:
        print(f"Error: {e}")
