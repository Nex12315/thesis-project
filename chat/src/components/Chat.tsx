// src/components/Chat.tsx
import React, { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { sendQuery, checkApiHealth } from "../services/api";
import { Message, ApiStatus } from "../types";

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [apiStatus, setApiStatus] = useState<ApiStatus>("checking");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on component mount
  useEffect(() => {
    const checkHealth = async () => {
      const isHealthy = await checkApiHealth();
      setApiStatus(isHealthy ? "healthy" : "unhealthy");

      // Add welcome message if API is healthy
      if (isHealthy) {
        setMessages([
          {
            text: "Welcome to the Arctic Valley AI Advisor! How can I help you with your business simulation project?",
            isUser: false,
            sources: [],
          },
        ]);
      }
    };

    checkHealth();
  }, []);

  // Auto-scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    // Add user message to chat
    setMessages((prev) => [...prev, { text, isUser: true }]);
    setIsLoading(true);

    try {
      // Send query to API
      const response = await sendQuery(text);

      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        {
          text: response.answer,
          isUser: false,
          sources: response.sources || [],
        },
      ]);
    } catch (error) {
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          text: `Sorry, I encountered an error. ${error} Please try again later.`,
          isUser: false,
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Display API status message if unhealthy
  if (apiStatus === "checking") {
    return <div className="loading">Connecting to AI service...</div>;
  }

  if (apiStatus === "unhealthy") {
    return (
      <div className="api-error">
        <h2>Cannot connect to the AI service</h2>
        <p>
          Please make sure the AI service is running at http://localhost:8000
        </p>
      </div>
    );
  }

  // Add welcome message if API is healthy
  if (isHealthy) {
    setMessages([
      {
        text: "Welcome to the Arctic Valley AI Advisor! How can I help you with your business simulation project?",
        isUser: false,
      },
    ]);
  }

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} isUser={message.isUser} />
        ))}
        {isLoading && (
          <div className="loading-indicator">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default Chat;
