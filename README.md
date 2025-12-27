# ☕ Coffee Management System

A **microservices-based coffee shop management system** built using **Python (Flask)**, **gRPC**, **REST APIs**, **MySQL**, and **Docker**.

This project demonstrates a **real-world distributed architecture**, where services are fully decoupled and communicate through well-defined interfaces.

---

## 🚀 Features

- **Gateway Service**
  - Central entry point for the system
  - Handles authentication, sessions, and request routing

- **Login Service**
  - Handles user authentication

- **Admin Login Service**
  - Dedicated authentication service for admins
  - Session-based admin access control

- **Menu Service**
  - Manages coffee menu items

- **Order Service**
  - Handles customer orders

- **Inventory Service**
  - Tracks stock and ingredients

- **Cafe Service**
  - Manages cafe locations and details

- **Analytics Service**
  - Provides sales analytics and dashboard metrics

- **Frontend**
  - Web-based interface (HTML, CSS, JavaScript)
  - Communicates only with the Gateway

---

## ⚙️ Technologies Used

- **Backend:** Python, Flask  
- **Communication:** REST APIs, gRPC (Protocol Buffers)  
- **Database:** MySQL  
- **Containerization:** Docker, Docker Compose  
- **Frontend:** HTML, CSS, JavaScript  
- **Version Control:** Git, GitHub  

---

## 🧩 Ports Overview

| Service               | Description                       | Port   |
|-----------------------|-----------------------------------|--------|
| Gateway               | Central API Gateway               | 5000   |
| Login Service         | User authentication               | 5001   |
| Order Service         | Order management                  | 5002   |
| Analytics Service     | Sales & analytics                 | 5003   |
| Cafe Service          | Cafe management                   | 5004   |
| Menu Service          | Menu operations                   | 5005   |
| Inventory Service     | Inventory management              | 5006   |
| Admin Login Service   | Admin authentication              | 50011  |
| MySQL Database        | Database container                | 3307   |
| Frontend              | Web interface                     | 8080   |

---

## 🐳 Running the Project

### Prerequisites
- Docker
- Docker Compose

### Steps

1. Clone the repository:
```bash
git clone https://github.com/fatimIB/coffee-management-system.git
cd coffee-management-system
```

2. Build and start all services:
```bash
docker-compose up --build
```

3. Access the system:
   - **Frontend:** http://localhost:8080
   - **Gateway API:** http://localhost:5000

4. Stop the containers:
```bash
docker-compose down
```

---

## 🔗 System Communication Architecture (REST & gRPC)

This project uses a hybrid communication architecture combining REST APIs and gRPC, where each protocol is used according to its strengths.

### 🌐 External Communication: REST (Frontend ↔ Gateway)

The frontend communicates only with the Gateway

- Communication uses HTTP + JSON
- JavaScript fetch() is used on the frontend
- REST is used because browsers cannot consume gRPC directly

**Examples:**
- Login & admin login
- Dashboard analytics
- Orders, menu, inventory, cafes
- Session validation & logout

```
Frontend  →  REST (HTTP + JSON)  →  Gateway
```

### 🚪 Gateway (Central Entry Point)

The Gateway is the core of the system.

**Responsibilities:**
- Exposes REST endpoints to the frontend
- Manages user and admin sessions
- Validates requests
- Translates REST requests into gRPC calls
- Aggregates responses when needed

The gateway never contains business logic.

### ⚡ Internal Communication: gRPC (Gateway ↔ Microservices)

All backend services communicate only via gRPC

- gRPC uses Protocol Buffers (.proto files)
- Services are strongly typed and independent

**gRPC-enabled services:**
- Login Service
- Admin Login Service
- Analytics Service
- Order Service
- Menu Service
- Inventory Service
- Cafe Service

```
Gateway  →  gRPC  →  Microservice
```

### 🔄 Example Flow: Admin Login

```
1. Frontend sends POST /adminlogin (REST)
2. Gateway receives the request
3. Gateway calls Admin Login Service via gRPC
4. Admin Login Service validates credentials
5. gRPC response is returned
6. Gateway creates a session
7. REST JSON response sent back to frontend
```

### 📊 Analytics Flow

```
Frontend
   ↓ REST
Gateway
   ↓ gRPC
Analytics Service
   ↓ gRPC
Gateway
   ↓ REST (JSON)
Dashboard
```

The frontend is completely unaware of gRPC.

---

## 🔐 Sessions & Security

- Sessions are handled only in the Gateway
- Backend services remain stateless
- Sensitive data is never exposed to the frontend
- Configuration is handled using environment variables

---

## 🚫 Technologies Not Used

- ❌ WebSockets (intentionally removed)
- ❌ Direct frontend → microservice communication
- ❌ gRPC exposed to the browser

---

## 🧪 Testing

### Current State
- Manual testing through the frontend
- API behavior verified via real user flows
- Container-level testing using Docker Compose

### Recommended Future Tests
- Unit tests for each microservice
- gRPC service tests
- Gateway integration tests
- Authentication & authorization tests
- End-to-end tests (frontend → gateway → services)

---

## 🧠 Architecture Summary

```
[ Frontend ]
     |
     |  REST (HTTP + JSON)
     v
[ Gateway ]
     |
     |  gRPC (Protocol Buffers)
     v
[ Microservices ]
(Login, AdminLogin, Orders, Menu, Inventory, Cafe, Analytics)
```

This architecture follows real industry microservices patterns, ensuring:

- Scalability
- Security
- Clean separation of concerns
- Maintainability

---

## 🧑‍💻 Author

- **Fatima Iboubkarne**
- Data Analytics & AI Student
- Distributed Systems Project

---

## 📜 License

This project is for educational purposes only.

Feel free to fork and modify it for learning or academic use.
