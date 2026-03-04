package com.liftlens.repository;

import com.liftlens.model.Analysis;
import com.liftlens.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface AnalysisRepository extends JpaRepository<Analysis, Long> {
    List<Analysis> findByUserOrderByCreatedAtDesc(User user);
    Optional<Analysis> findByIdAndUser(Long id, User user);
}
