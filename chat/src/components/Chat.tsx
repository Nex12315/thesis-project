// src/components/Chat.tsx
import React, { useState, useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import { sendStreamingQuery, checkApiHealth } from "../services/api";
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
      // Add a placeholder message for the AI response
      setMessages((prev) => [
        ...prev,
        {
          text: "", // Start with empty text
          isUser: false,
          isStreaming: true, // This triggers the loading dots animation
          sources: [],
        },
      ]);

      // Use streaming query
      await sendStreamingQuery(
        text,
        4,
        // On each chunk, update the message
        (chunk) => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const aiMessage = newMessages[newMessages.length - 1];

            newMessages[newMessages.length - 1] = {
              ...aiMessage,
              text: aiMessage.text + chunk,
            };

            return newMessages;
          });
        },
        // On done, remove the streaming status
        () => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const aiMessage = newMessages[newMessages.length - 1];

            newMessages[newMessages.length - 1] = {
              ...aiMessage,
              isStreaming: false, // This removes the loading dots
            };

            return newMessages;
          });
          setIsLoading(false);
        },
        // On error
        (error) => {
          setMessages((prev) => {
            const newMessages = [...prev];
            const aiMessage = newMessages[newMessages.length - 1];

            newMessages[newMessages.length - 1] = {
              ...aiMessage,
              text: `Sorry, I encountered an error: ${error}`,
              isStreaming: false,
            };

            return newMessages;
          });
          setIsLoading(false);
        }
      );
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

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} isUser={message.isUser} />
        ))}
        {isLoading && !messages[messages.length - 1]?.isStreaming && (
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
