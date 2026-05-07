import { Filters, QueryResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function submitQuery(
  question: string,
  filters?: Filters
): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, filters }),
  });

  if (!response.ok) {
    throw new Error(`Query failed: ${response.statusText}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<{
  status: string;
  papers_indexed: number;
}> {
  const response = await fetch(`${API_URL}/api/health`);
  return response.json();
}
