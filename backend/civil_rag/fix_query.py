import re

with open('graph_builder.py', 'r') as f:
    content = f.read()

# Fix the query_relationships method
old_query = '''            result = session.run(
                """
                MATCH (c:Concept {name: $concept})
                MATCH (c)-[:RELATED_TO*1..{depth}]-(related)
                RETURN DISTINCT related.name as concept, 
                       length(path) as distance
                ORDER BY distance, concept
                LIMIT 20
                """,
                concept=concept.lower(), depth=depth
            )'''

new_query = '''            result = session.run(
                """
                MATCH (c:Concept {name: $concept})
                MATCH (c)-[:RELATED_TO*1..2]-(related)
                RETURN DISTINCT related.name as concept, 
                       length(path) as distance
                ORDER BY distance, concept
                LIMIT 20
                """,
                concept=concept.lower()
            )'''

if old_query in content:
    content = content.replace(old_query, new_query)
    with open('graph_builder.py', 'w') as f:
        f.write(content)
    print("✅ Fixed query syntax")
else:
    print("⚠️ Query pattern not found, checking file...")
