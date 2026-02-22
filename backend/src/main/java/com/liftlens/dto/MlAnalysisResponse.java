package com.liftlens.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
public class MlAnalysisResponse {

    @JsonProperty("exercise_id")
    private String exerciseId;

    @JsonProperty("overall_score")
    private String overallScore;

    private List<MlFeedbackItem> feedback;
}
