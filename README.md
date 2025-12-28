# ☕ Coffee Management System

Distributed Microservices Application

---

## 📌 Project Overview

The Coffee Management System is a distributed microservices-based application designed to manage the operations of a coffee shop chain.
The system follows a client–gateway–microservices architecture, where each business domain is implemented as an independent service.

The project was developed as part of an academic course on Distributed Systems, with a strong focus on:

- Distributed communication (REST & gRPC)
- Service separation
- Integration testing
- Performance evaluation

---

## 🎯 Project Objectives

- Design and implement a distributed architecture
- Use REST for frontend communication
- Use gRPC for inter-service communication
- Ensure scalability, modularity, and maintainability
- Implement testing (unit, integration, performance)
- Demonstrate real-world microservices concepts

---

## 🧩 System Architecture

### Architectural Style

- Microservices architecture
- API Gateway pattern
- Client–Server model
- Stateless services

Each microservice:

- Runs independently
- Exposes gRPC endpoints
- Communicates with a shared MySQL database

---

## 🛠 Technologies Used

### Backend

- Python
- Flask
- gRPC & Protocol Buffers

### Frontend

- HTML
- CSS
- JavaScript

### Database

- MySQL

### DevOps & Tools

- Docker
- Docker Compose
- Git & GitHub
- pytest (testing)
- requests & grpcio (clients)

---

## 🚀 Microservices Description

| Service              | Responsibility                      |
|----------------------|-------------------------------------|
| Gateway              | Central entry point, routes REST requests to gRPC services     |
|                      |                                     |
| Login Service        | User authentication                 |
| Admin Login Service  | Admin authentication                |
| Cafe Service         | Cafe creation and management        |
| Menu Service         | Menu item management                |
| Inventory Service    | Stock management and restocking     |
| Order Service        | Order creation and processing       |
| Analytics Service    | Sales and performance analytics     |
| Frontend             | User & admin interface              |

---

## 🔌 Ports Configuration

| Service              | Port  |
|----------------------|------ |
| Gateway              | 5000  |
| Login Service        | 5001  |
| Order Service        | 5002  |
| Analytics Service    | 5003  |
| Cafe Service         | 5004  |
| Menu Service         | 5005  |
| Inventory Service    | 5006  |
| Admin Login Service  | 50011 |
| Frontend             | 8080  |
| MySQL                | 3307  |

---

## 🔄 Communication Model

### 1️⃣ Frontend → Gateway (REST)

Communication uses HTTP REST

Data exchanged in JSON

Handles:
- Login
- Orders
- Menu display
- Inventory viewing
- Analytics

**Example:**

```
POST /api/login
GET  /analytics
POST /orders/create
```

### 2️⃣ Gateway → Microservices (gRPC)

Gateway communicates with services using gRPC

Uses Protocol Buffers

**Advantages:**
- Fast communication
- Strong typing
- Clear service contracts

**Example:**
- Gateway → Order Service
- Order Service → Inventory Service

### 3️⃣ Database Access

- Each microservice connects to MySQL
- Credentials provided through environment variables
- Ensures separation of concerns

---

## 📊 Communication Flow Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                         Docker Compose                                │
│            (Single Virtual Network – Service Names DNS)               │
│                                                                       │
│  ┌──────────────────────────┐                                         │
│  │        Frontend          │                                         │
│  │   (HTML / CSS / JS)      │                                         │
│  │    Docker Container      │                                         │
│  └─────────────┬────────────┘                                         │
│                │                                                      │
│                │ REST (HTTP / JSON)                                   │
│                ▼                                                      │
│  ┌──────────────────────────────────────────┐                         │
│  │            API Gateway Container         │                         │
│  │                                          │                         │
│  │  ┌───────────────┐    ┌────────────────┐ │                         │
│  │  │    app.py     │──▶ |  gRPC Clients │ │                         │
│  │  │ (REST Routes) │    │ (client stubs) │ │                         │
│  │  └───────────────┘    └────────────────┘ │                         │
│  │                                          │                         │
│  └─────────────┬────────────────────────────┘                         │
│                │                                                      │
│                │ gRPC (Protocol Buffers)                              │
│                ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │                  Backend Microservices                        │    │
│  │                (One Docker Container per Service)             │    │
│  │                                                               │    │
│  │  ┌──────────────┐   ┌────────────────┐   ┌──────────────┐     │    │
│  │  │ Login        │   │ Admin Login    │   │ Cafe         │     │    │
│  │  │ Service      │   │ Service        │   │ Service      │     │    │
│  │  │ (Flask+gRPC) │   │ (Flask+gRPC)   │   │ (Flask+gRPC) │     │    │
│  │  └──────────────┘   └────────────────┘   └──────────────┘     │    │
│  │                                                               │    │
│  │  ┌──────────────┐   ┌────────────────┐   ┌──────────────┐     │    │
│  │  │ Menu         │   │ Inventory      │   │ Order        │     │    │
│  │  │ Service      │   │ Service        │   │ Service      │     │    │
│  │  │ (Flask+gRPC) │   │ (Flask+gRPC)   │   │ (Flask+gRPC) │     │    │
│  │  └──────────────┘   └────────────────┘   └──────────────┘     │    │
│  │                                                               │    │
│  │  ┌────────────────┐                                           │    │
│  │  │ Analytics      │                                           │    │
│  │  │ Service        │                                           │    │
│  │  │ (Flask+gRPC)   │                                           │    │
│  │  └────────────────┘                                           │    │
│  └─────────────┬─────────────────────────────────────────────────┘    │
│                │                                                      │
│                │ SQL Queries                                          │
│                ▼                                                      │
│  ┌──────────────────────────┐                                         │
│  │      MySQL Database      │                                         │
│  │     Docker Container     │                                         │
│  └──────────────────────────┘                                         │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Strategy

Testing was a core part of this project.

### ✅ Unit Tests

Implemented using pytest:

- Login service tests
- Admin login tests
- Menu service tests
- Cafe service tests
- Inventory service tests
- Orders service tests
- Analytics service tests

Each test verifies:
- Correct response codes
- Valid data returned
- Error handling

### 🔗 Integration Tests

- Frontend → Gateway communication
- Gateway → gRPC service calls
- Validation of complete request flow

**Example:**

Login request from frontend → Gateway → Login Service → Database

### ⚡ Performance Tests

A dedicated performance test script was implemented:

- Sends multiple REST and gRPC requests
- Measures:
  - Average response time
  - Minimum response time
  - Maximum response time
  - Tests system behavior under repeated requests

**Performance metrics include:**
- REST services performance
- gRPC services performance
- Gateway response times

⚠️ **Note:** Some order requests may fail due to inventory constraints; however, response-time measurements remain valid for performance evaluation.

---

## 🐳 Running the Project (Docker)

### Prerequisites

- Docker
- Docker Compose

### Steps

1. Clone the repository:

```bash
git clone https://github.com/fatimIB/coffee-management-system.git
cd coffee-management-system
```

2. Build and run the application:

```bash
docker-compose up --build
```

3. Access the system:

   - **Frontend:** http://localhost:8080
   - **Gateway API:** http://localhost:5000
   - **MySQL:** localhost:3307

4. Stop the containers:

```bash
docker-compose down
```

---

## 👥 Team Members

- **Fatima Iboubkarne** – Project Lead & Developer
- **Faris Amina** – Developer
- **Abdelkbir Chouiter** – Developer
- **Salma Jeghloul** – Developer
- **Ayoub El Orf** – Developer
- **Ismail Dakir** – Developer

---

## 📚 Academic Context

This project was developed for educational purposes as part of a course on Distributed Systems.
It demonstrates practical implementation of:

- Microservices
- gRPC
- REST APIs
- Testing strategies
- Performance evaluation

---

## 📜 License

Educational use only.

