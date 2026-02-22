package com.liftlens.controller;

import com.liftlens.dto.AnalysisResponse;
import com.liftlens.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/analyses")
@RequiredArgsConstructor
public class AnalysisController {

    private final AnalysisService analysisService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<AnalysisResponse> create(
            @RequestParam("exercise_id") String exerciseId,
            @RequestParam("video") MultipartFile video
    ) throws IOException {
        return ResponseEntity.ok(analysisService.create(video, exerciseId));
    }

    @GetMapping
    public ResponseEntity<List<AnalysisResponse>> getAll() {
        return ResponseEntity.ok(analysisService.getAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnalysisResponse> getById(@PathVariable Long id) {
        return ResponseEntity.ok(analysisService.getById(id));
    }
}
