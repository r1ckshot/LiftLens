import type { Analysis } from "@/types/analysis";
import type { AuthResponse } from "@/types/auth";
import { getToken, clearToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    clearToken();
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API error (${res.status}): ${text}`);
  }
  return res.json();
}

export async function register(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `Registration failed (${res.status})`);
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `Login failed (${res.status})`);
  }
  return res.json();
}

export function analyzeVideo(
  video: File,
  exerciseId: string,
  onProgress?: (percent: number) => void,
  signal?: AbortSignal
): Promise<Analysis> {
  return new Promise((resolve, reject) => {
    const token = getToken();
    const formData = new FormData();
    formData.append("video", video);
    formData.append("exercise_id", exerciseId);

    const xhr = new XMLHttpRequest();

    if (signal) {
      signal.addEventListener("abort", () => {
        xhr.abort();
        reject(new DOMException("Analysis cancelled", "AbortError"));
      });
    }

    // Upload phase: 0-60% of total progress
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 60));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 401) {
        clearToken();
        window.location.href = "/login";
        reject(new Error("Unauthorized"));
        return;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        if (onProgress) onProgress(100);
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          reject(new Error("Invalid response from server"));
        }
      } else {
        let msg = `API error (${xhr.status})`;
        try {
          const body = JSON.parse(xhr.responseText);
          if (body.error) msg = `API error (${xhr.status}): ${body.error}`;
        } catch { /* ignore */ }
        reject(new Error(msg));
      }
    };

    xhr.onerror = () => reject(new Error("Network error. Check your connection."));

    xhr.open("POST", `${API_URL}/api/analyses`);
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.send(formData);
  });
}

export async function getAnalyses(): Promise<Analysis[]> {
  const res = await fetch(`${API_URL}/api/analyses`, {
    headers: authHeaders(),
  });
  return handleResponse<Analysis[]>(res);
}

export async function getAnalysisById(id: number): Promise<Analysis> {
  const res = await fetch(`${API_URL}/api/analyses/${id}`, {
    headers: authHeaders(),
  });
  return handleResponse<Analysis>(res);
}

export async function deleteAnalysis(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/api/analyses/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) {
    clearToken();
    window.location.href = "/login";
    return;
  }
  if (!res.ok) throw new Error(`Delete failed (${res.status})`);
}

export async function deleteAllAnalyses(): Promise<void> {
  const res = await fetch(`${API_URL}/api/analyses`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (res.status === 401) {
    clearToken();
    window.location.href = "/login";
    return;
  }
  if (!res.ok) throw new Error(`Clear failed (${res.status})`);
}

export function skeletonVideoUrl(id: number): string {
  const token = getToken();
  return `${API_URL}/api/analyses/${id}/skeleton-video${token ? `?token=${token}` : ""}`;
}
