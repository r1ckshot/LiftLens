from app.pose_estimator import PoseEstimator
from app.feature_extractor import FeatureExtractor
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem
from app.classifiers.squat import SquatClassifier

_CLASSIFIERS: dict[str, BaseClassifier] = {
    "squat": SquatClassifier(),
}


class Analyzer:
    """Runs the full analysis pipeline: video → landmarks → features → classification."""

    def __init__(self):
        self._pose = PoseEstimator()
        self._extractor = FeatureExtractor()

    def analyze(self, video_path: str, exercise_id: str) -> ClassificationResult:
        classifier = _CLASSIFIERS.get(exercise_id)
        if classifier is None:
            return ClassificationResult(
                overall_score="poor",
                feedback=[FeedbackItem(
                    "general", "error",
                    f"Exercise '{exercise_id}' is not yet supported.",
                )],
            )

        landmarks_seq = self._pose.process_video(video_path)
        features_seq = self._extractor.extract_sequence(landmarks_seq)
        return classifier.predict(features_seq)

    def close(self):
        self._pose.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
