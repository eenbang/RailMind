import type {
  AssistantParseResult,
  RecommendationResult,
  TravelRequest
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function requestJson<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.error?.message ?? `请求失败 (${response.status})`);
  }

  return response.json() as Promise<T>;
}

export function fetchRecommendations(
  request: TravelRequest,
  limit = 3
): Promise<RecommendationResult> {
  return requestJson("/api/v1/recommendations", {
    method: "POST",
    body: JSON.stringify({ request, limit, include_candidates: false })
  });
}

export function parseTravelRequest(text: string): Promise<AssistantParseResult> {
  return requestJson("/api/v1/assistant/parse", {
    method: "POST",
    body: JSON.stringify({ text })
  });
}
