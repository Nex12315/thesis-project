// src/services/api.ts
import axios from "axios";
import { QueryResponse, HealthResponse } from "../types";

const API_URL = "http://localhost:8000"; // Change to your API URL

export const sendQuery = async (
  query: string,
  maxContextDocs = 4
): Promise<QueryResponse> => {
  try {
    const response = await axios.post<QueryResponse>(`${API_URL}/query`, {
      query,
      max_context_docs: maxContextDocs,
    });
    return response.data;
  } catch (error) {
    console.error("Error querying the AI:", error);
    throw error;
  }
};

// Add a new function to handle streaming
export const sendStreamingQuery = async (
  query: string,
  maxContextDocs = 4,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (error: string) => void
): Promise<void> => {
  try {
    const response = await fetch(`${API_URL}/query-stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        max_context_docs: maxContextDocs,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Create a reader to handle the stream
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        break;
      }

      // Decode the chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process events in buffer
      const events = buffer.split("\n\n");
      buffer = events.pop() || ""; // Keep the last incomplete event in the buffer

      for (const event of events) {
        if (event.startsWith("data: ")) {
          try {
            const data = JSON.parse(event.substring(6));

            if (data.type === "content") {
              onChunk(data.data);
            } else if (data.type === "done") {
              onDone();
            } else if (data.type === "error") {
              onError(data.data);
            }
          } catch (e) {
            console.error("Error parsing event data:", e);
          }
        }
      }
    }
  } catch (error) {
    console.error("Error with streaming query:", error);
    onError(`Error: ${error}`);
  }
};

export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get<HealthResponse>(`${API_URL}/health`);
    return response.data.status === "healthy";
  } catch (error) {
    console.error("API health check failed:", error);
    return false;
  }
};
