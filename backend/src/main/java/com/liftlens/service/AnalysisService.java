package com.liftlens.service;

import com.liftlens.dto.AnalysisResponse;
import com.liftlens.dto.FeedbackItemResponse;
import com.liftlens.dto.MlAnalysisResponse;
import com.liftlens.model.Analysis;
import com.liftlens.model.FeedbackItem;
import com.liftlens.model.FeedbackStatus;
import com.liftlens.model.OverallScore;
import com.liftlens.repository.AnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AnalysisService {

    private static final Map<String, String> EXERCISE_MUSCLE_GROUP = Map.ofEntries(
            Map.entry("bench_press", "chest"),
            Map.entry("incline_bench_press", "chest"),
            Map.entry("push_up", "chest"),
            Map.entry("overhead_press", "shoulders"),
            Map.entry("lateral_raise", "shoulders"),
            Map.entry("arnold_press", "shoulders"),
            Map.entry("squat", "legs"),
            Map.entry("lunge", "legs"),
            Map.entry("bulgarian_split_squat", "legs"),
            Map.entry("romanian_deadlift", "legs"),
            Map.entry("pull_up", "back"),
            Map.entry("barbell_row", "back"),
            Map.entry("deadlift", "back")
    );

    private final AnalysisRepository analysisRepository;
    private final MlService mlService;

    @Value("${app.video-storage-path}")
    private String videoStoragePath;

    public AnalysisResponse create(MultipartFile video, String exerciseId) throws IOException {
        String muscleGroup = EXERCISE_MUSCLE_GROUP.getOrDefault(exerciseId, "unknown");

        String filename = UUID.randomUUID() + "_" + video.getOriginalFilename();
        Path storedPath = Path.of(videoStoragePath, filename);
        Files.createDirectories(storedPath.getParent());
        Files.copy(video.getInputStream(), storedPath);

        MlAnalysisResponse mlResult = mlService.analyze(storedPath, exerciseId);

        Analysis analysis = Analysis.builder()
                .exerciseId(exerciseId)
                .muscleGroup(muscleGroup)
                .overallScore(OverallScore.valueOf(mlResult.getOverallScore()))
                .videoPath(storedPath.toString())
                .skeletonVideoPath(mlResult.getSkeletonVideoPath())
                .build();

        List<FeedbackItem> items = mlResult.getFeedback().stream()
                .map(f -> FeedbackItem.builder()
                        .analysis(analysis)
                        .aspect(f.getAspect())
                        .status(FeedbackStatus.valueOf(f.getStatus()))
                        .message(f.getMessage())
                        .build())
                .toList();

        analysis.setFeedbackItems(items);
        Analysis saved = analysisRepository.save(analysis);
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<AnalysisResponse> getAll() {
        return analysisRepository.findAll().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public AnalysisResponse getById(Long id) {
        return analysisRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + id));
    }

    @Transactional(readOnly = true)
    public String getSkeletonVideoPath(Long id) {
        return analysisRepository.findById(id)
                .map(Analysis::getSkeletonVideoPath)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + id));
    }

    private AnalysisResponse toResponse(Analysis a) {
        List<FeedbackItemResponse> feedback = a.getFeedbackItems() == null
                ? List.of()
                : a.getFeedbackItems().stream()
                        .map(f -> new FeedbackItemResponse(f.getId(), f.getAspect(), f.getStatus().name(), f.getMessage()))
                        .toList();

        return new AnalysisResponse(
                a.getId(),
                a.getExerciseId(),
                a.getMuscleGroup(),
                a.getOverallScore().name(),
                a.getVideoPath(),
                a.getSkeletonVideoPath(),
                a.getCreatedAt(),
                feedback
        );
    }
}
