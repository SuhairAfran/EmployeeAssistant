// lib/api.ts — Frontend API client for the FastAPI backend

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "/api/v1";

// Derive the root URL for health checks.
// If the base URL is relative (/api/v1), health is at /health.
// If absolute (http://localhost:8000/api/v1), strip the path.
const API_ROOT_URL = API_BASE_URL.startsWith("http")
  ? API_BASE_URL.replace(/\/api\/v1\/?$/, "")
  : "";

/**
 * Helper to build auth headers.
 * In DEBUG mode the backend reads `X-Mock-Role` to synthesise a mock user.
 * In production, replace with a real Bearer token.
 */
const getHeaders = (role: string): Record<string, string> => ({
  "Content-Type": "application/json",
  "X-Mock-Role": role,
});

/**
 * Shared fetch wrapper with better error messages.
 */
async function apiFetch<T>(
  url: string,
  options: RequestInit
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, options);
  } catch (networkError) {
    throw new Error(
      "Cannot reach the backend server. Make sure the FastAPI backend is running on " +
        API_ROOT_URL
    );
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON — use statusText
    }
    throw new Error(`API Error (${response.status}): ${detail}`);
  }

  return response.json() as Promise<T>;
}

// ── Type definitions matching the backend Pydantic models ────────────────────

export type ChatApiResponse = {
  response: string;
  session_id: string;
  intent: string;
  agent_used: string | null;
  approval_required: boolean;
  metadata: Record<string, unknown>;
};

export type ApprovalApiResponse = {
  status: string;
  decision: string;
  session_id: string;
};

export type HealthResponse = {
  status: string;
  db: boolean;
  app?: string;
  env?: string;
  debug?: boolean;
};

// ── API methods ──────────────────────────────────────────────────────────────

export const api = {
  /**
   * Quick check that the backend is reachable.
   */
  health: async (): Promise<HealthResponse> => {
    return apiFetch<HealthResponse>(`${API_ROOT_URL}/health`, {
      method: "GET",
    });
  },

  /**
   * Send a chat message to the LangGraph workflow.
   */
  chat: async (
    message: string,
    sessionId: string | null,
    role: string
  ): Promise<ChatApiResponse> => {
    return apiFetch<ChatApiResponse>(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  },

  /**
   * Submit a manager's approval/rejection decision for a paused workflow.
   */
  approve: async (
    sessionId: string,
    decision: "approved" | "rejected",
    note: string,
    role: string
  ): Promise<ApprovalApiResponse> => {
    return apiFetch<ApprovalApiResponse>(`${API_BASE_URL}/approve`, {
      method: "POST",
      headers: getHeaders(role),
      body: JSON.stringify({
        session_id: sessionId,
        decision,
        note,
      }),
    });
  },
};