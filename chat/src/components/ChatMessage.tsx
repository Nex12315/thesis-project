import React, { useEffect, useState } from "react";
import { Message } from "../types";

interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser }) => {
  const [cursorVisible, setCursorVisible] = useState(true);

  // Add blinking cursor effect for streaming messages
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    if (message.isStreaming) {
      interval = setInterval(() => {
        setCursorVisible((prev) => !prev);
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
          {message.isStreaming && cursorVisible && (
            <span className="cursor">|</span>
          )}
        </p>
      </div>
    </div>
  );
};

export default ChatMessage;
