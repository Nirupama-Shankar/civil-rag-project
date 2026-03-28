# Add this to api.py - replace the ask_question function

from .agentic_controller import init_agentic, get_agentic

# Initialize agentic controller when app starts
@app.on_event("startup")
async def startup_event():
    init_agentic(ollama)
    print("🤖 Agentic AI Controller initialized")

@app.post("/ask_agentic", response_model=QueryResponse)
async def ask_agentic_question(req: QueryRequest):
    """Ask question using Agentic AI with planning and reflection"""
    
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    session_id = req.session_id
    if not session_id:
        session_id = memory.create_session()
    
    memory.add_message("user", req.query, session_id)
    
    print(f"\n🤖 AGENTIC MODE: {req.query}")
    
    # Get agentic controller
    agentic = get_agentic()
    
    # STEP 1: PLAN
    print("📋 Creating plan...")
    plan = agentic.plan(req.query)
    print(f"   Steps: {len(plan.get('steps', []))}")
    
    # STEP 2: EXECUTE
    print("⚙️ Executing plan...")
    def retrieval_func(query, tool):
        tools = [tool]
        docs = hybrid_retrieval(query, text_store, dataset_store, image_store, tools)
        return docs
    
    results = agentic.execute(plan, req.query, retrieval_func)
    
    # STEP 3: REFLECT
    print("🤔 Reflecting on results...")
    reflection = agentic.reflect(results, plan)
    
    # STEP 4: PREPARE CONTEXT
    all_docs = []
    for result in results:
        all_docs.extend(result.get("documents", []))
    
    if not all_docs:
        answer = "No relevant information found."
        sources = []
    else:
        # Deduplicate
        seen = set()
        unique_docs = []
        for doc in all_docs:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
        
        context = "\n\n".join([f"[Source: {doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in unique_docs[:5]])
        
        # STEP 5: GENERATE ANSWER
        answer = agentic.answer(req.query, context, plan, results)
        
        # Add reflection insights if needed
        if not reflection.get("sufficient", True):
            answer += f"\n\n💡 *Note: {reflection.get('missing', 'More information would help provide a complete answer.')}*"
        
        sources = list({doc.metadata.get("source", "Unknown") for doc in unique_docs[:5]})
    
    memory.add_message("assistant", answer, session_id)
    
    return QueryResponse(
        answer=answer,
        tools=["agentic_planning"],
        sources=sources,
        session_id=session_id
    )
