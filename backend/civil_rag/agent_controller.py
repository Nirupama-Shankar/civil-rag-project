"""
Agent Controller - Dynamically routes queries to appropriate tools
Now supports ANY document type (civil engineering, algorithms, etc.)
"""

import re

VALID_TOOLS = {"text_search", "dataset_search", "image_search", "ocr_search"}

TOOL_DESCRIPTIONS = """
- text_search      : search text content (PDF, DOCX, TXT) - for ANY topic
- dataset_search   : search CSV datasets for numerical analysis
- image_search     : search diagrams, drawings, images
- ocr_search       : search scanned/image-based PDFs
"""

def _parse_tools(response_text: str) -> list[str]:
    """Extract tool names from LLM output"""
    text = response_text.lower()
    found = [tool for tool in VALID_TOOLS if tool in text]
    return found if found else ["text_search"]

def agent_plan(query: str, llm) -> list[str]:
    """
    Route query to appropriate tools using LLM.
    Now handles ANY document type - civil, algorithms, etc.
    """
    prompt = f"""You are a routing agent for a document question-answering system.

Available tools:
{TOOL_DESCRIPTIONS}

Rules:
- Choose ONLY from the tool names above
- You may choose more than one
- Reply with ONLY the tool names, comma-separated
- ALWAYS include text_search for ANY text-based question

Question: {query}

Tools:"""

    try:
        response = llm.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response["message"]["content"]
        tools = _parse_tools(raw)
        print(f"🧠 Agent tools: {tools}")
        return tools
    except Exception as e:
        print(f"⚠️ Agent planning failed: {e}. Defaulting to text_search.")
        return ["text_search"]

def simple_route(query: str) -> str:
    """Simple keyword-based routing (fallback)"""
    query_lower = query.lower()
    
    image_keywords = ["diagram", "figure", "image", "draw", "sketch", "illustration", "picture", "photo"]
    dataset_keywords = ["predict", "estimate", "calculate", "strength", "data", "analysis", "value", "csv", "dataset"]
    
    if any(word in query_lower for word in image_keywords):
        return "image"
    elif any(word in query_lower for word in dataset_keywords):
        return "dataset"
    else:
        return "text"
