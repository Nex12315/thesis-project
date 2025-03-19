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

export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get<HealthResponse>(`${API_URL}/health`);
    return response.data.status === "healthy";
  } catch (error) {
    console.error("API health check failed:", error);
    return false;
  }
};
