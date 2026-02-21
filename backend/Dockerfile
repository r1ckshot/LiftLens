# Stage 1: Build
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests -B

# Stage 2: Runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

RUN mkdir -p /app/videos /app/skeleton_videos

COPY --from=build /build/target/*.jar app.jar

RUN apk add --no-cache curl

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
