"""
Conversation Memory Module
Stores chat history for contextual conversations
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
import os

class ConversationMemory:
    def __init__(self, max_history: int = 10):
        """Initialize conversation memory"""
        self.max_history = max_history
        self.sessions = {}  # session_id -> list of messages
        self.current_session = None
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new conversation session"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.current_session = session_id
        return session_id
    
    def add_message(self, role: str, content: str, session_id: str = None):
        """Add a message to conversation history"""
        if session_id is None:
            session_id = self.current_session
        
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessions[session_id].append(message)
        
        # Keep only last N messages
        if len(self.sessions[session_id]) > self.max_history * 2:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history * 2:]
    
    def get_history(self, session_id: str = None, last_n: int = None) -> List[Dict]:
        """Get conversation history"""
        if session_id is None:
            session_id = self.current_session
        
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]
        if last_n:
            return history[-last_n:]
        return history
    
    def get_context(self, session_id: str = None, last_n: int = 3) -> str:
        """Get formatted conversation context for LLM"""
        history = self.get_history(session_id, last_n)
        
        if not history:
            return ""
        
        context_parts = ["Previous conversation:"]
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear_session(self, session_id: str = None):
        """Clear conversation history"""
        if session_id is None:
            session_id = self.current_session
        
        if session_id in self.sessions:
            self.sessions[session_id] = []
            return True
        return False

# Global instance
memory = ConversationMemory()
