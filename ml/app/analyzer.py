from dataclasses import dataclass
from typing import Optional

from app.pose_estimator import PoseEstimator
from app.feature_extractor import FeatureExtractor
from app.classifiers.base import BaseClassifier, ClassificationResult, FeedbackItem
from app.classifiers.squat import SquatClassifier
from app.classifiers.push_up import PushUpClassifier
from app.classifiers.lunge import LungeClassifier
from app.classifiers.pull_up import PullUpClassifier
from app.camera_validator import check_side_view
from app.skeleton_renderer import SkeletonRenderer

_CLASSIFIERS: dict[str, BaseClassifier] = {
    "squat": SquatClassifier(),
    "push_up": PushUpClassifier(),
    "lunge": LungeClassifier(),
    "pull_up": PullUpClassifier(),
}


@dataclass
class AnalysisResult:
    classification: ClassificationResult
    skeleton_video_path: Optional[str]


class Analyzer:
    """Runs the full analysis pipeline: video → landmarks → features → classification → skeleton."""

    def __init__(self):
        self._pose = PoseEstimator()
        self._extractor = FeatureExtractor()
        self._renderer = SkeletonRenderer()

    def analyze(
        self,
        video_path: str,
        exercise_id: str,
        skeleton_output_path: Optional[str] = None,
    ) -> AnalysisResult:
        classifier = _CLASSIFIERS.get(exercise_id)
        if classifier is None:
            return AnalysisResult(
                classification=ClassificationResult(
                    overall_score="poor",
                    feedback=[FeedbackItem(
                        "general", "error",
                        f"Exercise '{exercise_id}' is not yet supported.",
                    )],
                ),
                skeleton_video_path=None,
            )

        landmarks_seq = self._pose.process_video(video_path)

        camera_error = check_side_view(landmarks_seq)
        if camera_error:
            return AnalysisResult(
                classification=ClassificationResult(
                    overall_score="poor",
                    feedback=[FeedbackItem("camera_angle", "error", camera_error)],
                ),
                skeleton_video_path=None,
            )

        features_seq = self._extractor.extract_sequence(landmarks_seq)
        classification = classifier.predict(features_seq)

        skeleton_path = None
        if skeleton_output_path is not None:
            self._renderer.render(video_path, landmarks_seq, skeleton_output_path)
            skeleton_path = skeleton_output_path

        return AnalysisResult(classification=classification, skeleton_video_path=skeleton_path)

    def close(self):
        self._pose.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
