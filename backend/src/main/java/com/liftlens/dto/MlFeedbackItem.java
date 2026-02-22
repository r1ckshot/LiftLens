package com.liftlens.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class MlFeedbackItem {
    private String aspect;
    private String status;
    private String message;
}
