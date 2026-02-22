package com.liftlens.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class FeedbackItemResponse {
    private Long id;
    private String aspect;
    private String status;
    private String message;
}
