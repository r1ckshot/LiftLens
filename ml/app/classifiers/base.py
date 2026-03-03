from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


def robust_min(vals: list[float], skip: int = 2) -> Optional[float]:
    """min() that ignores the `skip` smallest values to filter isolated MediaPipe artifact frames."""
    if not vals:
        return None
    s = sorted(vals)
    return s[min(skip, len(s) - 1)]


def robust_max(vals: list[float], skip: int = 2) -> Optional[float]:
    """max() that ignores the `skip` largest values to filter isolated MediaPipe artifact frames."""
    if not vals:
        return None
    s = sorted(vals, reverse=True)
    return s[min(skip, len(s) - 1)]


@dataclass
class FeedbackItem:
    aspect: str
    status: str   # 'ok' | 'warning' | 'error'
    message: str


@dataclass
class ClassificationResult:
    overall_score: str              # 'good' | 'needs_improvement' | 'poor'
    feedback: list[FeedbackItem] = field(default_factory=list)


class BaseClassifier(ABC):
    """Abstract base classifier for exercise technique evaluation."""

    @abstractmethod
    def predict(self, features) -> ClassificationResult:
        """Predict technique quality from a sequence of FrameFeatures."""
        pass
