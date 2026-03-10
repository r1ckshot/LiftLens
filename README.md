# 🏋️ LiftLens

**AI-powered exercise form analyzer.** Upload a workout video, select your exercise, and get instant feedback on your technique — powered by MediaPipe pose estimation, Spring Boot, and Next.js.

<table>
  <td><img src="https://github.com/user-attachments/assets/cb468c0b-97ae-4819-b547-517cc0784b42" /></td>
</table>

## ✨ Features

### 🎥 Video Upload & Exercise Selection
- Drag-and-drop or click to upload (MP4, MOV, AVI — up to 500 MB)
- 12 exercises across 4 muscle groups: Legs, Chest, Shoulders, Back
- Camera angle hint shown inline per exercise (Side view / Front view / Any angle)
- Analyze button enabled only when both a file and an exercise are selected

<table>
  <td><img src="https://github.com/user-attachments/assets/e819b4ed-1893-4404-9301-af75ff26c757" /></td>
</table>

### 🎯 AI Form Analysis
- MediaPipe Pose detects 33 body landmarks on every frame
- Rule-based classifier measures joint angles against biomechanical thresholds
- Overall score: **Good** / **Needs Improvement** / **Poor**
- Detailed feedback items per aspect (depth, knee alignment, back position, elbow angle, etc.)
- Wrong camera angle detected and reported with a clear error card

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/dcf2900a-b031-4480-86de-ce743bd52f79" /></td>
    <td><img src="https://github.com/user-attachments/assets/bcce34e1-51b8-44cd-9bdd-abff8f2d69b2" /></td>
  </tr>
</table>

### 📹 Skeleton Visualization
- Annotated skeleton overlay drawn on the processed video
- Problematic joints highlighted in orange/red
- Video playable directly in the browser

> I appear in the video below — because the best apps are the ones you'd actually want to use yourself.

<table>
  <td><img src="https://github.com/user-attachments/assets/226b6851-c915-417e-ba57-553ae916ba47" /></td>
</table>

### 📊 Analysis History
- All past analyses saved per account
- Browse by date with score badges at a glance
- Replay any skeleton video inline
- Delete all history with one click

<table>
  <td><img src="https://github.com/user-attachments/assets/0c91a558-c974-4545-9aff-da00fd0a7ee6" /></td>
</table>

### 🔐 Authentication
- Register and log in with email + password
- JWT-based auth with 7-day token
- All analyses are private and tied to your account

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d63bf75b-b7f2-4882-9f4f-ceb4db4f4822" /></td>
    <td><img src="https://github.com/user-attachments/assets/3ad89ab7-0a7b-49cd-bb44-0b2ce1633de7" /></td>
  </tr>
</table>

## 🛠️ Technologies

### Frontend
![Next.js](https://img.shields.io/badge/Next.js-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

### Backend
![Java](https://img.shields.io/badge/Java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-%236DB33F.svg?style=for-the-badge&logo=springboot&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white)

### ML Service
![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![OpenCV](https://img.shields.io/badge/OpenCV-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0097A7?style=for-the-badge&logoColor=white)

### DevOps
![Docker](https://img.shields.io/badge/Docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## 🚀 Getting Started

### Prerequisites

- Docker Engine 20.10+ and Docker Compose 2.0+
- ~6 GB RAM (ML service is memory-intensive)
- ~8 GB disk space (ML image alone is ~5 GB due to MediaPipe + PyTorch dependencies)

### Running with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/r1ckshot/LiftLens.git
   cd LiftLens
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```
   Edit `.env` and set your own values:
   ```env
   MYSQL_ROOT_PASSWORD=your_root_password
   MYSQL_DATABASE=liftlens_db
   MYSQL_USER=liftlens
   MYSQL_PASSWORD=your_password
   JWT_SECRET=your_secret_key_minimum_32_characters_long
   ```
   `frontend/.env` is pre-configured for local Docker and doesn't need changes.

3. **Build and start all services**
   ```bash
   docker-compose up --build
   ```
   > The first build downloads ~5 GB of ML dependencies — subsequent builds are fast.

4. **Access the application**
   - App: `http://localhost:3000`
   - ML health check: `http://localhost:8000`

## 📚 What I Learned

This project is where I first worked with computer vision and AI integration in a real application:

### 🧠 Pose Estimation & Computer Vision
- How pose estimation models work — landmark detection as a feature extraction layer
- Building a rule-based classifier on top of pre-trained model output (joint angles → feedback)
- Full video processing pipeline: decode frames → run inference → annotate → re-encode
- MediaPipe's video tracking mode — why frame 0 behaves differently than subsequent frames

### 🏗️ Three-Service Microservices Architecture
- Coordinating three independent services (Next.js, Spring Boot, FastAPI) that communicate over HTTP
- Docker Compose health checks and `depends_on: condition: service_healthy` for startup ordering
- Shared Docker volumes for inter-service file passing (skeleton videos)

## 🤖 AI-Assisted Development

- **Me** — architecture decisions, exercise selection, threshold calibration, design direction, and review
- **Claude Sonnet 4.6** — writing the majority of the code based on my requirements and feedback

> *"AI assists me, but the decisions are mine."*

## 👨‍💻 Author

**Mykhailo Kapustianyk**
- GitHub: [@r1ckshot](https://github.com/r1ckshot)
- Year: 2026

---
