// src/components/ChatMessage.tsx
import React from "react";
import { Message } from "../types";

interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  return (
    <div className={`chat-message ${isUser ? "user-message" : "ai-message"}`}>
      <div className="message-avatar">{isUser ? "👤" : "🤖"}</div>
      <div className="message-content">
        <p>{message.text}</p>
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <small>Sources:</small>
            <ul>
              {message.sources.map((source, index) => (
                <li key={index}>{source.title}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
