import React from "react";
import { motion } from "framer-motion";

function ChatMessage({ msg }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={msg.role === "user" ? "user-msg" : "bot-msg"}
    >
      <div>{msg.text}</div>

      {msg.role === "bot" && (
        <div className="meta">
          <details>
            <summary>🧠 Agent Thinking</summary>
            <p>Tools: {msg.tools?.join(", ")}</p>
          </details>

          <p>📌 Sources: {msg.sources?.join(", ")}</p>
        </div>
      )}
    </motion.div>
  );
}

export default ChatMessage;