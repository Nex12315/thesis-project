import React, { useEffect, useState } from "react";
import { Message } from "../types";

interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  const [dots, setDots] = useState(".");

  // Create animated dots when streaming
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    if (message.isStreaming) {
      interval = setInterval(() => {
        setDots((prev) => {
          if (prev === ".") return "..";
          if (prev === "..") return "...";
          return ".";
        });
      }, 500);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [message.isStreaming]);

  return (
    <div className={`chat-message ${isUser ? "user-message" : "ai-message"}`}>
      <div className="message-avatar">{isUser ? "👤" : "🤖"}</div>
      <div className="message-content">
        <p>
          {message.text}
          {message.isStreaming && <span className="loading-dots">{dots}</span>}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;
