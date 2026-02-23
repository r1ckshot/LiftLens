package com.liftlens.controller;

import com.liftlens.dto.AnalysisResponse;
import com.liftlens.service.AnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
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

    /**
     * Streams the skeleton video with proper HTTP Range support.
     * Range requests are required by all browsers for HTML5 <video> seeking.
     */
    @GetMapping("/{id}/skeleton-video")
    public ResponseEntity<StreamingResponseBody> getSkeletonVideo(
            @RequestHeader HttpHeaders headers,
            @PathVariable Long id) throws IOException {

        String videoPath = analysisService.getSkeletonVideoPath(id);
        if (videoPath == null) return ResponseEntity.notFound().build();

        Path filePath = Path.of(videoPath);
        if (!Files.exists(filePath)) return ResponseEntity.notFound().build();

        long fileSize = Files.size(filePath);
        List<HttpRange> ranges = headers.getRange();

        final long start;
        final long end;
        final HttpStatus status;

        if (ranges.isEmpty()) {
            start = 0;
            end = fileSize - 1;
            status = HttpStatus.OK;
        } else {
            HttpRange range = ranges.get(0);
            start = range.getRangeStart(fileSize);
            end = range.getRangeEnd(fileSize);
            status = HttpStatus.PARTIAL_CONTENT;
        }

        long length = end - start + 1;

        StreamingResponseBody body = outputStream -> {
            try (FileInputStream fis = new FileInputStream(filePath.toFile())) {
                fis.skip(start);
                byte[] buf = new byte[65536];
                long remaining = length;
                while (remaining > 0) {
                    int read = fis.read(buf, 0, (int) Math.min(buf.length, remaining));
                    if (read == -1) break;
                    outputStream.write(buf, 0, read);
                    remaining -= read;
                }
            } catch (IOException e) {
                // Suppress broken pipe — client closed the connection (normal for video seeking)
                String msg = e.getMessage();
                if (msg == null || (!msg.contains("Broken pipe") && !msg.contains("Connection reset"))) {
                    throw e;
                }
            }
        };

        ResponseEntity.BodyBuilder builder = ResponseEntity.status(status)
                .contentType(MediaType.parseMediaType("video/mp4"))
                .header(HttpHeaders.ACCEPT_RANGES, "bytes")
                .header(HttpHeaders.CONTENT_LENGTH, String.valueOf(length));

        if (status == HttpStatus.PARTIAL_CONTENT) {
            builder.header(HttpHeaders.CONTENT_RANGE,
                    String.format("bytes %d-%d/%d", start, end, fileSize));
        }

        return builder.body(body);
    }
}
