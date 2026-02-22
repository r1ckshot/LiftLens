package com.liftlens.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@AllArgsConstructor
public class AnalysisResponse {
    private Long id;
    private String exerciseId;
    private String muscleGroup;
    private String overallScore;
    private String videoPath;
    private String skeletonVideoPath;
    private LocalDateTime createdAt;
    private List<FeedbackItemResponse> feedbackItems;
}
