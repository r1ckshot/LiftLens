package com.liftlens.service;

import com.liftlens.dto.MlAnalysisResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.nio.file.Path;

@Service
@RequiredArgsConstructor
public class MlService {

    private final RestTemplate restTemplate;

    @Value("${app.ml-service-url}")
    private String mlServiceUrl;

    public MlAnalysisResponse analyze(Path videoPath, String exerciseId) {
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("exercise_id", exerciseId);
        body.add("video", new FileSystemResource(videoPath));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
        ResponseEntity<MlAnalysisResponse> response = restTemplate.postForEntity(
                mlServiceUrl + "/analyze", request, MlAnalysisResponse.class
        );
        return response.getBody();
    }
}
