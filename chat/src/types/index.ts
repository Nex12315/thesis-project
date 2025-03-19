// Message-related types
export interface Message {
  text: string;
  isUser: boolean;
  isStreaming?: boolean;
}

export interface Source {
  title: string;
  source: string;
}

// API-related types
export interface QueryRequest {
  query: string;
  max_context_docs?: number;
}

export interface QueryResponse {
  answer: string;
}

export interface HealthResponse {
  status: string;
}

// API status type
export type ApiStatus = "checking" | "healthy" | "unhealthy";
