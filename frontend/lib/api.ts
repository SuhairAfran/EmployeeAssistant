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
 * Helper to build auth headers using a JWT bearer token.
 * Pass `null` only for public endpoints.
 */
const getHeaders = (token: string | null): Record<string, string> => {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
};

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

// ── Approvals (in-app, manager dashboard) ─────────────────────────────────────

export type EntityType = "leave" | "asset" | "reimbursement";

export type PendingItem = {
  entity_type: EntityType;
  entity_id: string;
  employee_id: string;
  employee_name: string;
  employee_designation: string | null;
  submitted_at: string;
  // type-specific fields (sparse)
  leave_type?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  business_days?: number | null;
  asset_type?: string | null;
  justification?: string | null;
  claim_no?: string | null;
  category?: string | null;
  amount?: number | null;
  currency?: string | null;
  description?: string | null;
  reason?: string | null;
};

export type PendingResponse = {
  count: number;
  items: PendingItem[];
};

export type DecideResponse = {
  status: string;
  entity_type: EntityType;
  entity_id: string;
  new_status: string;
};

// ── Self-service ──────────────────────────────────────────────────────────────

export type LeaveBalanceItem = {
  leave_type: string;
  entitled_days: number;
  used_days: number;
  pending_days: number;
  carried_over: number;
  available_days: number;
};

export type LeaveHistoryItem = {
  id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  business_days: number;
  status: string;
  reason: string | null;
  applied_at: string;
  reviewer_note: string | null;
};

export type ITTicketItem = {
  id: string;
  ticket_no: string;
  category: string;
  subject: string;
  priority: string;
  status: string;
  created_at: string;
  resolution: string | null;
};

export type TeamLeaveTodayItem = {
  user_id: string;
  full_name: string;
  designation: string | null;
  leave_type: string;
  end_date: string;
};

export type ActivityItem = {
  kind: "leave" | "ticket";
  title: string;
  status: string;
  when: string;
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
    token: string | null
  ): Promise<ChatApiResponse> => {
    return apiFetch<ChatApiResponse>(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  },

  /**
   * Stream a chat response token-by-token via Server-Sent Events.
   *
   * Calls `onToken` for each incremental text chunk and `onDone` once with
   * the final metadata. `onError` is called if the stream fails.
   */
  chatStream: async (
    message: string,
    sessionId: string | null,
    token: string | null,
    callbacks: {
      onToken: (token: string) => void;
      onDone: (meta: ChatApiResponse) => void;
      onError: (err: string) => void;
    },
    signal?: AbortSignal,
  ): Promise<void> => {
    let response: Response;
    try {
      response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: "POST",
        headers: getHeaders(token),
        body: JSON.stringify({ message, session_id: sessionId }),
        signal,
      });
    } catch (err) {
      callbacks.onError(
        err instanceof Error ? err.message : "Network error",
      );
      return;
    }

    if (!response.ok || !response.body) {
      callbacks.onError(`API Error (${response.status}): ${response.statusText}`);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE messages are separated by a blank line.
        let sepIndex: number;
        while ((sepIndex = buffer.indexOf("\n\n")) !== -1) {
          const rawEvent = buffer.slice(0, sepIndex).trim();
          buffer = buffer.slice(sepIndex + 2);
          if (!rawEvent.startsWith("data:")) continue;
          const jsonStr = rawEvent.replace(/^data:\s*/, "");
          if (!jsonStr) continue;
          try {
            const evt = JSON.parse(jsonStr);
            if (evt.type === "token") {
              callbacks.onToken(evt.content || "");
            } else if (evt.type === "done") {
              callbacks.onDone(evt as ChatApiResponse);
            } else if (evt.type === "error") {
              callbacks.onError(evt.message || "Unknown error");
            }
          } catch {
            // ignore malformed events
          }
        }
      }
    } catch (err) {
      callbacks.onError(
        err instanceof Error ? err.message : "Stream read error",
      );
    }
  },

  /**
   * Fetch chat history for a session ID
   */
  chatHistory: async (
    sessionId: string,
    token: string | null
  ): Promise<{ messages: { role: string; content: string; id: string }[] }> => {
    return apiFetch<{ messages: { role: string; content: string; id: string }[] }>(`${API_BASE_URL}/chat/history/${sessionId}`, {
      method: "GET",
      headers: getHeaders(token),
    });
  },

  // ── Approvals ──────────────────────────────────────────────────────────────

  pendingApprovals: async (token: string | null): Promise<PendingResponse> => {
    return apiFetch<PendingResponse>(`${API_BASE_URL}/approvals/pending`, {
      method: "GET",
      headers: getHeaders(token),
    });
  },

  pendingApprovalsCount: async (
    token: string | null,
  ): Promise<{ count: number }> => {
    return apiFetch<{ count: number }>(`${API_BASE_URL}/approvals/count`, {
      method: "GET",
      headers: getHeaders(token),
    });
  },

  decideApproval: async (
    entityType: EntityType,
    entityId: string,
    decision: "approve" | "reject",
    note: string,
    token: string | null,
  ): Promise<DecideResponse> => {
    return apiFetch<DecideResponse>(`${API_BASE_URL}/approvals/decide`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({
        entity_type: entityType,
        entity_id: entityId,
        decision,
        note,
      }),
    });
  },

  // ── Self-service ───────────────────────────────────────────────────────────

  myLeaveBalance: async (
    token: string | null,
    year?: number,
  ): Promise<LeaveBalanceItem[]> => {
    const qs = year ? `?year=${year}` : "";
    return apiFetch<LeaveBalanceItem[]>(`${API_BASE_URL}/me/leave-balance${qs}`, {
      method: "GET",
      headers: getHeaders(token),
    });
  },

  myLeaveHistory: async (
    token: string | null,
    limit = 50,
  ): Promise<LeaveHistoryItem[]> => {
    return apiFetch<LeaveHistoryItem[]>(
      `${API_BASE_URL}/me/leave-history?limit=${limit}`,
      { method: "GET", headers: getHeaders(token) },
    );
  },

  myITTickets: async (
    token: string | null,
    limit = 50,
  ): Promise<ITTicketItem[]> => {
    return apiFetch<ITTicketItem[]>(
      `${API_BASE_URL}/me/it-tickets?limit=${limit}`,
      { method: "GET", headers: getHeaders(token) },
    );
  },

  teamLeavesToday: async (
    token: string | null,
  ): Promise<TeamLeaveTodayItem[]> => {
    return apiFetch<TeamLeaveTodayItem[]>(
      `${API_BASE_URL}/me/team/leaves-today`,
      { method: "GET", headers: getHeaders(token) },
    );
  },

  recentActivity: async (
    token: string | null,
    limit = 8,
  ): Promise<ActivityItem[]> => {
    return apiFetch<ActivityItem[]>(
      `${API_BASE_URL}/me/recent-activity?limit=${limit}`,
      { method: "GET", headers: getHeaders(token) },
    );
  },
};