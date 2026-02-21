package com.liftlens.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class MlService {

    @Value("${app.ml-service-url}")
    private String mlServiceUrl;
}
