from abc import ABC, abstractmethod
from dataclasses import dataclass, field


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
