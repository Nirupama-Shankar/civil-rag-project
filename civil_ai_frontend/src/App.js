import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./index.css";
// Add to App.js
import ForceGraph2D from 'react-force-graph-2d';

function GraphViewer({ concept }) {
  const [graphData, setGraphData] = useState(null);
  
  useEffect(() => {
    fetch(`http://localhost:8000/graph/${concept}`)
      .then(res => res.json())
      .then(data => setGraphData(data));
  }, [concept]);
  
  if (!graphData) return <div>Loading graph...</div>;
  
  return (
    <ForceGraph2D
      graphData={graphData}
      nodeLabel="id"
      nodeColor={(node) => node.group === 1 ? '#ff6b6b' : '#4ecdc4'}
      linkWidth={2}
      linkColor={() => '#888'}
    />
  );
}

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [agentMode, setAgentMode] = useState("standard");
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          role: "bot",
          text: "Hello! I'm your Civil Engineering AI Assistant. I have three modes:\n\n⚡ **Standard Mode** - Fast answers from documents\n🤖 **Agentic Mode** - Plans and executes complex queries\n🎯 **Multi-Agent Mode** - 7 specialized agents working together\n\nAsk me about concrete mix design, construction standards, or upload your own documents!"
        }
      ]);
    }
  }, []);

  const searchImages = async (query) => {
    try {
      const res = await axios.post("http://localhost:8000/search_images", {
        query: query
      });
      console.log("📸 API Response:", res.data);
      return res.data.images || [];
    } catch (error) {
      console.error("Image search error:", error);
      return [];
    }
  };

  const sendQuery = async () => {
    if (!query.trim()) return;

    const userMsg = { role: "user", text: query };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      // Check if this is an image-related query
      const imageKeywords = ['diagram', 'figure', 'image', 'picture', 'show', 'display', 'drawing', 'photo', 'images'];
      const isImageQuery = imageKeywords.some(keyword => query.toLowerCase().includes(keyword));
      
      let imageResults = [];
      if (isImageQuery) {
        console.log("🔍 Searching images for:", query);
        imageResults = await searchImages(query);
        console.log("📸 Found images:", imageResults.length);
      }
      
      // Get text answer from AI
      let endpoint;
      if (agentMode === "standard") {
        endpoint = "/ask";
      } else if (agentMode === "agentic") {
        endpoint = "/ask_agentic";
      } else {
        endpoint = "/ask_agentic_v2";
      }
      
      const res = await axios.post(`http://localhost:8000${endpoint}`, {
        query: query,
        session_id: sessionId
      });

      if (res.data.session_id) {
        setSessionId(res.data.session_id);
      }

      // Create bot message - images are stored separately in imageGallery
      const botMsg = {
        role: "bot",
        text: res.data.answer,  // Only text answer here
        tools: agentMode === "standard" ? res.data.tools : 
               agentMode === "agentic" ? ["🤖 Agentic Planning"] : ["🎯 Multi-Agent Orchestrator"],
        sources: res.data.sources || [],
        question: query,
        timestamp: new Date().toISOString(),
        imageGallery: imageResults  // Images stored separately
      };

      setMessages((prev) => [...prev, botMsg]);
      
    } catch (error) {
      console.error("API Error:", error);
      const errorMsg = {
        role: "bot",
        text: "⚠️ Failed to connect to the AI assistant. Please make sure the backend server is running."
      };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setLoading(false);
  };

  const exportToPDF = async (msg) => {
    if (!msg.question) return;
    
    try {
      const response = await axios.post(
        "http://localhost:8000/export_pdf",
        {
          question: msg.question,
          answer: msg.text,
          sources: msg.sources
        },
        { responseType: "blob" }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `civil_ai_answer_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error("Export Error:", error);
      alert("Failed to export PDF");
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      if (res.data.success) {
        const successMsg = {
          role: "bot",
          text: `✅ Document uploaded successfully! I've ingested "${file.name}" and can now answer questions about it.`
        };
        setMessages((prev) => [...prev, successMsg]);
      } else {
        throw new Error(res.data.error);
      }
    } catch (error) {
      console.error("Upload Error:", error);
      const errorMsg = {
        role: "bot",
        text: `❌ Failed to upload document: ${error.response?.data?.error || error.message}`
      };
      setMessages((prev) => [...prev, errorMsg]);
    }

    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const clearConversation = async () => {
    if (sessionId) {
      try {
        await axios.post("http://localhost:8000/clear_session", null, {
          params: { session_id: sessionId }
        });
      } catch (error) {
        console.error("Clear session error:", error);
      }
    }
    setSessionId(null);
    setMessages([
      {
        role: "bot",
        text: "Conversation cleared! How can I help you with civil engineering today?"
      }
    ]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  };

  const getModeDescription = () => {
    switch(agentMode) {
      case "standard":
        return "⚡ Fast answers from documents";
      case "agentic":
        return "🤖 Plans, executes, and reflects";
      default:
        return "🎯 7 specialized agents working together";
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1 className="title">
          <span className="title-icon">🏗️</span>
          Civil Engineering AI Agent
        </h1>
        <p className="subtitle">{getModeDescription()}</p>
        
        <div className="mode-selector">
          <button 
            className={agentMode === "standard" ? "mode-active" : "mode-btn"}
            onClick={() => setAgentMode("standard")}
          >
            ⚡ Standard
          </button>
          <button 
            className={agentMode === "agentic" ? "mode-active" : "mode-btn"}
            onClick={() => setAgentMode("agentic")}
          >
            🤖 Agentic
          </button>
          <button 
            className={agentMode === "multi" ? "mode-active" : "mode-btn"}
            onClick={() => setAgentMode("multi")}
          >
            🎯 Multi-Agent
          </button>
        </div>
        
        <div className="header-buttons">
          <label className="upload-btn">
            📄 Upload Document
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".pdf,.docx,.txt,.csv"
              style={{ display: "none" }}
              disabled={uploading}
            />
          </label>
          <button onClick={clearConversation} className="clear-btn">
            🗑️ Clear Conversation
          </button>
        </div>
        {uploading && <p className="upload-status">📤 Uploading and ingesting document...</p>}
      </div>

      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === 'user' ? 'user-msg' : 'bot-msg'}>
            <div className="message-content">
              <strong>{msg.role === 'user' ? '👤 You:' : 
                msg.mode === 'multi' ? '🎯 Multi-Agent AI' :
                msg.mode === 'agentic' ? '🤖 Agentic AI' : '🤖 Civil AI'}</strong>
              <div className="message-text">
                {msg.text.split('\n').map((line, idx) => (
                  <React.Fragment key={idx}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </div>
              
              {/* IMAGE GALLERY - Display actual images */}
              {msg.imageGallery && msg.imageGallery.length > 0 && (
                <div className="image-gallery">
                  <strong>📸 Found {msg.imageGallery.length} images:</strong>
                  <div className="image-grid">
                    {msg.imageGallery.map((img, idx) => (
                      <div key={idx} className="image-card">
                        <img 
                          src={`http://localhost:8000/image/${encodeURIComponent(img.filename)}`}
                          alt={img.filename}
                          className="thumbnail"
                          onClick={() => window.open(`http://localhost:8000/image/${img.filename}`, '_blank')}
                          onError={(e) => {
                            console.error('Failed to load image:', img.filename);
                            e.target.style.display = 'none';
                            e.target.parentElement.innerHTML = '<div style="padding:40px;text-align:center">⚠️ Image not found</div>';
                          }}
                        />
                        <div className="image-caption">{img.filename.substring(0, 30)}...</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {msg.tools && msg.tools.length > 0 && (
                <div className="tools-used">
                  🔧 Tools: {msg.tools.map((t, idx) => (
                    <span key={idx} className="tool-tag">{t}</span>
                  ))}
                </div>
              )}
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="sources">
                  📚 Sources: {msg.sources.map((s, idx) => (
                    <div key={idx} className="source-item">• {s}</div>
                  ))}
                </div>
              )}
              
              {msg.role === 'bot' && msg.question && (
                <div className="export-btn-container">
                  <button 
                    onClick={() => exportToPDF(msg)} 
                    className="export-btn"
                  >
                    📥 Export as PDF
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="thinking">
            {agentMode === "multi" ? "🎯 Multi-Agent System is planning and executing..." : 
             agentMode === "agentic" ? "🤖 Agentic AI is thinking and planning..." : 
             "🤖 Thinking..."}
          </div>
        )}

        <div ref={chatEndRef}></div>
      </div>

      <div className="input-box">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={agentMode === "multi" ? 
            "Ask a complex question - 7 agents will collaborate to answer..." : 
            agentMode === "agentic" ?
            "Ask a question - Agentic AI will plan, execute, and reflect..." :
            "Ask about concrete strength, mix design, standards... or upload a document!"}
          disabled={loading || uploading}
        />
        <button onClick={sendQuery} disabled={loading || uploading || !query.trim()}>
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}

export default App;
