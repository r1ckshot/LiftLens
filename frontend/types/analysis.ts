export type OverallScore = "good" | "needs_improvement" | "poor";

export type FeedbackStatus = "ok" | "warning" | "error";

export interface FeedbackItem {
  id: number;
  aspect: string;
  status: FeedbackStatus;
  message: string;
}

export interface Analysis {
  id: number;
  exerciseId: string;
  muscleGroup: string;
  overallScore: OverallScore;
  skeletonVideoPath: string | null;
  createdAt: string;
  feedbackItems: FeedbackItem[];
}
