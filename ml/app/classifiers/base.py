"""Base class for exercise technique classifiers."""

from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    """Abstract base classifier for exercise technique evaluation."""

    @abstractmethod
    def predict(self, features):
        """Predict technique quality from extracted features."""
        pass
