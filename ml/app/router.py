import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.analyzer import Analyzer
from app.exercises import EXERCISES
from service_config import SKELETON_OUTPUT_DIR

router = APIRouter()

_analyzer = Analyzer()

_ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


class FeedbackItemOut(BaseModel):
    aspect: str
    status: str
    message: str


class AnalysisOut(BaseModel):
    exercise_id: str
    overall_score: str
    feedback: list[FeedbackItemOut]
    skeleton_video_path: Optional[str]


@router.post("/analyze", response_model=AnalysisOut)
def analyze(
    exercise_id: str = Form(...),
    video: UploadFile = File(...),
):
    if exercise_id not in EXERCISES:
        raise HTTPException(status_code=400, detail=f"Unknown exercise: '{exercise_id}'")

    suffix = Path(video.filename or "video.mp4").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: '{suffix}'")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(video.file, tmp)
        tmp_path = tmp.name

    SKELETON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    skeleton_path = str(SKELETON_OUTPUT_DIR / f"{uuid.uuid4()}_skeleton.mp4")

    try:
        result = _analyzer.analyze(tmp_path, exercise_id, skeleton_output_path=skeleton_path)
    finally:
        os.unlink(tmp_path)

    cl = result.classification
    return AnalysisOut(
        exercise_id=exercise_id,
        overall_score=cl.overall_score,
        feedback=[
            FeedbackItemOut(aspect=f.aspect, status=f.status, message=f.message)
            for f in cl.feedback
        ],
        skeleton_video_path=result.skeleton_video_path,
    )
