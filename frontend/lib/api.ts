import type { Analysis } from "@/types/analysis";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export async function analyzeVideo(
  video: File,
  exerciseId: string
): Promise<Analysis> {
  const formData = new FormData();
  formData.append("video", video);
  formData.append("exercise_id", exerciseId);

  const response = await fetch(`${API_URL}/api/analyses`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text().catch(() => response.statusText);
    throw new Error(`Analysis failed (${response.status}): ${text}`);
  }

  return response.json();
}

export async function getAnalyses(): Promise<Analysis[]> {
  const response = await fetch(`${API_URL}/api/analyses`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

export function skeletonVideoUrl(id: number): string {
  return `${API_URL}/api/analyses/${id}/skeleton-video`;
}
