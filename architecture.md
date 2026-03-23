# Chronic Disease Prediction AI Service Architecture

## Overview
This system is designed as a scalable, asynchronous AI inference architecture for chronic disease prediction.  
It separates API handling, authentication, task queuing, and AI inference into independent components using containerized services.

---

## High-Level Architecture

### Key Characteristics
- Microservice-based architecture
- Asynchronous processing (Queue-based)
- Scalable AI worker structure
- JWT-based authentication
- Container orchestration (Docker)

---

## Core Components

### 1. Client (User)
- Sends HTTPS requests via Web or API
- Performs:
  - Input data submission
  - Result retrieval (Task ID or Key-based)

---

### 2. NGINX (Entry Point)
Role:
- Reverse Proxy
- Load Balancer
- Static Asset Serving

Responsibilities:
- Receives HTTPS requests
- Routes API calls to FastAPI
- Handles authentication flow with external auth server

---

### 3. External Authentication Server (OAuth Provider)

Examples:
- Naver
- Kakao

Role:
- OAuth authentication
- JWT issuance

Flow:
1. User authenticates via OAuth
2. JWT token is issued
3. Token is used in subsequent API requests

---

### 4. FastAPI (API Gateway & Producer)

Role:
- API Gateway
- Authentication validation (JWT)
- Task producer
- Final report generation

Responsibilities:
- Validate incoming requests
- Package user input data
- Dispatch AI inference tasks to Redis
- Retrieve results and generate final report

---

### 5. Redis (Message Broker & Result Store)

Role:
- Message Broker
- Task Queue Manager
- Result Cache Store

Components:
- Task Queue
  - Stores incoming inference tasks
- Result Store
  - Stores inference results
  - Supports TTL (Time-To-Live)

Key Mechanisms:
- LPUSH → Task enqueue
- BRPOP → Worker task consumption

---

### 6. AI Workers (Consumer Layer)

Structure:
- Scalable (1 ~ N workers)

Role:
- Consume tasks from Redis queue
- Perform model inference

Responsibilities:
- Load pre-trained model
- Execute inference
- Store results back into Redis

---

## Workflow

### 1. Access & Authentication
1. User sends HTTPS request
2. Request passes through NGINX
3. OAuth authentication via external server
4. JWT token issued and attached to requests

---

### 2. Service Request Processing
1. User sends data (with JWT)
2. NGINX forwards request to FastAPI
3. FastAPI:
   - Validates JWT
   - Packages input data
   - Generates Task ID

---

### 3. Asynchronous Inference
1. FastAPI pushes task to Redis (LPUSH)
2. AI Worker pulls task (BRPOP)
3. Worker:
   - Loads model
   - Performs inference
   - Stores result in Redis

---

### 4. Result Retrieval

Two approaches:

#### 4.1 Polling
- User queries using Task ID
- FastAPI fetches result from Redis

#### 4.2 Push / Key-Based Retrieval
- Result stored with a key
- FastAPI retrieves and returns final report

---

## Data Flow Summary

User → NGINX → FastAPI → Redis Queue → AI Worker  
     ←        ←         ← Redis Result Store

---

## Design Advantages

### Scalability
- AI workers can scale horizontally (1 → N)

### Performance
- Heavy inference tasks are offloaded from API server

### Reliability
- Queue-based processing prevents request blocking

### Flexibility
- Supports both polling and push-based result retrieval

### Security
- OAuth + JWT-based authentication

---

## Potential Improvements

- Add monitoring (Prometheus / Grafana)
- Introduce retry mechanism for failed tasks
- Use distributed queue (Kafka, RabbitMQ) for large-scale systems
- Implement model versioning & A/B testing
- Add caching layer optimization

---

## Conclusion

This architecture effectively separates concerns between:
- Request handling
- Authentication
- Task processing
- AI inference

By adopting an asynchronous queue-based model, it ensures high scalability, reliability, and performance for AI-driven services.
