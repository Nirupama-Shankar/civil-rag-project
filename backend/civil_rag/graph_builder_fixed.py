    def query_relationships(self, concept: str, depth: int = 2) -> Dict:
        """Query graph for related concepts"""
        with self.driver.session() as session:
            # For now, use fixed depth 2
            result = session.run(
                """
                MATCH (c:Concept {name: $concept})
                MATCH (c)-[:RELATED_TO*1..2]-(related)
                RETURN DISTINCT related.name as concept, 
                       length(path) as distance
                ORDER BY distance, concept
                LIMIT 20
                """,
                concept=concept.lower()
            )
            
            relationships = []
            for record in result:
                relationships.append({
                    "concept": record["concept"],
                    "distance": record["distance"]
                })
            
            return {"concept": concept, "related": relationships}
