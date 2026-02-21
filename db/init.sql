USE liftlens_db;

CREATE TABLE IF NOT EXISTS analyses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    exercise_id VARCHAR(50) NOT NULL,
    muscle_group VARCHAR(50) NOT NULL,
    overall_score ENUM('good', 'needs_improvement', 'poor') NOT NULL,
    video_path VARCHAR(500),
    skeleton_video_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feedback_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    analysis_id BIGINT NOT NULL,
    aspect VARCHAR(100) NOT NULL,
    status ENUM('ok', 'warning', 'error') NOT NULL,
    message VARCHAR(500) NOT NULL,
    CONSTRAINT fk_feedback_analysis
        FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
