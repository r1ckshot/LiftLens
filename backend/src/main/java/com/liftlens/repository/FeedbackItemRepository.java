package com.liftlens.repository;

import com.liftlens.model.FeedbackItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FeedbackItemRepository extends JpaRepository<FeedbackItem, Long> {
}
