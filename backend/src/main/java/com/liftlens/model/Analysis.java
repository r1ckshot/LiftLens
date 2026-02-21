package com.liftlens.model;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "analyses")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Analysis {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "exercise_id", nullable = false, length = 50)
    private String exerciseId;

    @Column(name = "muscle_group", nullable = false, length = 50)
    private String muscleGroup;

    @Enumerated(EnumType.STRING)
    @Column(name = "overall_score", nullable = false)
    private OverallScore overallScore;

    @Column(name = "video_path", length = 500)
    private String videoPath;

    @Column(name = "skeleton_video_path", length = 500)
    private String skeletonVideoPath;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "analysis", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<FeedbackItem> feedbackItems;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}
