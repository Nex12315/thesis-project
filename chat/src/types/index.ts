// Message-related types
export interface Message {
  text: string;
  isUser: boolean;
  sources?: Source[];
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
  sources: Source[];
}

export interface HealthResponse {
  status: string;
}

// API status type
export type ApiStatus = "checking" | "healthy" | "unhealthy";
