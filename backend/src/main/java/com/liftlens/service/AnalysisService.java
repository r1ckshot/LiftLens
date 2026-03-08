package com.liftlens.service;

import com.liftlens.dto.AnalysisResponse;
import com.liftlens.dto.FeedbackItemResponse;
import com.liftlens.dto.MlAnalysisResponse;
import com.liftlens.model.Analysis;
import com.liftlens.model.FeedbackItem;
import com.liftlens.model.FeedbackStatus;
import com.liftlens.model.OverallScore;
import com.liftlens.model.User;
import com.liftlens.repository.AnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
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
            Map.entry("upright_row", "shoulders"),
            Map.entry("squat", "legs"),
            Map.entry("lunge", "legs"),
            Map.entry("romanian_deadlift", "legs"),
            Map.entry("pull_up", "back"),
            Map.entry("barbell_row", "back"),
            Map.entry("deadlift", "back")
    );

    private final AnalysisRepository analysisRepository;
    private final MlService mlService;

    @Transactional
    public AnalysisResponse create(MultipartFile video, String exerciseId, User user) throws IOException {
        String muscleGroup = EXERCISE_MUSCLE_GROUP.getOrDefault(exerciseId, "unknown");

        Path tempFile = Files.createTempFile(UUID.randomUUID().toString(), "_" + video.getOriginalFilename());
        try {
            Files.copy(video.getInputStream(), tempFile, StandardCopyOption.REPLACE_EXISTING);
            MlAnalysisResponse mlResult = mlService.analyze(tempFile, exerciseId);

            // Camera angle error: return feedback without saving to the database
            boolean hasCameraError = mlResult.getFeedback().stream()
                    .anyMatch(f -> "camera_angle".equals(f.getAspect()));
            if (hasCameraError) {
                List<FeedbackItemResponse> cameraFeedback = mlResult.getFeedback().stream()
                        .map(f -> new FeedbackItemResponse(null, f.getAspect(), f.getStatus(), f.getMessage()))
                        .toList();
                return new AnalysisResponse(null, exerciseId, muscleGroup,
                        mlResult.getOverallScore(), null, java.time.LocalDateTime.now(), cameraFeedback);
            }

            Analysis analysis = Analysis.builder()
                    .user(user)
                    .exerciseId(exerciseId)
                    .muscleGroup(muscleGroup)
                    .overallScore(OverallScore.valueOf(mlResult.getOverallScore()))
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
        } finally {
            Files.deleteIfExists(tempFile);
        }
    }

    @Transactional(readOnly = true)
    public List<AnalysisResponse> getByUser(User user) {
        return analysisRepository.findByUserOrderByCreatedAtDesc(user).stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public AnalysisResponse getById(Long id, User user) {
        return analysisRepository.findByIdAndUser(id, user)
                .map(this::toResponse)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + id));
    }

    @Transactional
    public void delete(Long id, User user) {
        Analysis analysis = analysisRepository.findByIdAndUser(id, user)
                .orElseThrow(() -> new RuntimeException("Analysis not found: " + id));
        if (analysis.getSkeletonVideoPath() != null) {
            try {
                Files.deleteIfExists(Path.of(analysis.getSkeletonVideoPath()));
            } catch (IOException ignored) {
            }
        }
        analysisRepository.delete(analysis);
    }

    @Transactional
    public void deleteAll(User user) {
        List<Analysis> analyses = analysisRepository.findByUser(user);
        for (Analysis analysis : analyses) {
            if (analysis.getSkeletonVideoPath() != null) {
                try { Files.deleteIfExists(Path.of(analysis.getSkeletonVideoPath())); } catch (IOException ignored) {}
            }
        }
        analysisRepository.deleteAll(analyses);
    }

    @Transactional(readOnly = true)
    public String getSkeletonVideoPath(Long id, User user) {
        return analysisRepository.findByIdAndUser(id, user)
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
                a.getSkeletonVideoPath(),
                a.getCreatedAt(),
                feedback
        );
    }
}
