// lib/api.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Helper to get auth headers (In production, replace with actual JWT token)
const getHeaders = (role: string) => ({
  "Content-Type": "application/json",
  // We pass the role in a custom header just for testing purposes so your 
  // backend middleware can mock the user context.
  "X-Mock-Role": role, 
});

export const api = {
  chat: async (message: string, sessionId: string | null, role: string) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    return response.json();
  },

  approve: async (sessionId: string, decision: "approved" | "rejected", note: string, role: string) => {
    const response = await fetch(`${API_BASE_URL}/approve`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        session_id: sessionId,
        decision,
        note,
      }),
    });

    if (!response.ok) {
      throw new Error(`Approval Error: ${response.statusText}`);
    }
    return response.json();
  },
};