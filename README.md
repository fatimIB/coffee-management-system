# ☕ Coffee Management System

A **microservices-based coffee shop management system** built using **Python (Flask)**, **MySQL**, and **Docker**.  
This project demonstrates a distributed architecture where each feature runs as an independent service, communicating through **REST and gRPC**.

---

## 🚀 Features

- **Login Service:** Handles user authentication (login/signup).  
- **Admin Login Service:** Handles admin authentication.  
- **Menu Service:** Manages coffee menu items.  
- **Order Service:** Handles customer orders.  
- **Inventory Service:** Tracks stock and ingredients.  
- **Cafe Service:** Manages cafe locations and details.  
- **Analytics Service:** Generates sales and performance insights.  
- **Gateway:** Central API gateway routing requests to services.  
- **Frontend:** Web interface for users and admin.

---

## ⚙️ Technologies Used

- **Backend:** Python, Flask  
- **Database:** MySQL (connection through environment variables)  
- **Containerization:** Docker & Docker Compose  
- **Frontend:** HTML, CSS, JavaScript  
- **Communication:** REST (Frontend → Gateway), gRPC (Gateway → Services)  
- **Version Control:** Git & GitHub  

---

## 🧩 Ports Overview

| Service              | Description                  | Port  |
|----------------------|------------------------------|-------|
| Gateway              | Main API gateway             | 5000  |
| Login Service        | Handles user authentication  | 5001  |
| Admin Login Service  | Admin authentication         | 5011  |
| Order Service        | Manages customer orders      | 5002  |
| Analytics Service    | Sales and analytics          | 5003  |
| Cafe Service         | Cafe info and management     | 5004  |
| Menu Service         | Coffee menu operations       | 5005  |
| Inventory Service    | Stock management             | 5006  |
| MySQL Database       | Data storage (container)     | 3307  |
| Frontend             | Web interface                | 8080  |

---

## 🐳 Running the Project

Make sure you have **Docker** and **Docker Compose** installed.

1. Clone the repository:

```bash
git clone https://github.com/fatimIB/coffee-management-system.git
cd coffee-management-system
```

2. Build and run the containers:

```bash
docker-compose up --build
```

3. Access the system:

   - **Frontend:** http://localhost:8080
   - **Gateway API:** http://localhost:5000
   - **MySQL Database:** localhost:3307

4. Stop containers:

```bash
docker-compose down
```

---

## 🔄 How It Works (Communication Flow)

### 1. Frontend → Gateway (REST)

The frontend communicates with the gateway using REST HTTP requests (GET, POST, etc.).

Example: Fetching analytics data or sending login credentials.

### 2. Gateway → Microservices (gRPC)

The gateway communicates with each microservice using gRPC with Protocol Buffers:

- Sends structured requests
- Receives structured responses
- Converts gRPC responses to JSON for the frontend

### 3. Database Access

Each microservice connects to the MySQL database using environment variables for credentials.

### Communication Flow Diagram

```
[Frontend (Browser)] 
         |
         |  REST (HTTP JSON)
         v
[Gateway API] 
    |      |       |       |       |
    |      |       |       |       |
   gRPC   gRPC    gRPC    gRPC    gRPC
    v      v       v       v       v
[Login] [AdminLogin] [Menu] [Orders] [Analytics]
[Inventory] [Cafe]
    |
    v
[MySQL Database]
```

---

## 🧪 Manual Testing Performed

- **Database Connection Test:** Verified connection to MySQL before starting services.

- **Service Smoke Tests:** Opened each service in a browser by port to confirm it is running (e.g., http://localhost:5001 for Login Service).

- **Admin Login Flow:** Verified admin login works via frontend and session management.

- **Menu, Orders, Inventory, Analytics:** Verified CRUD operations through frontend interactions and gateway routing.

These are manual functional checks to ensure the system works correctly.

---

## 🧑‍💻 Contributors

- **Fatima Iboubkarne** – Project Lead & Developer
- **Faris Amina** – Developer
- **Abdelkbir Chouiter** – Developer
- **Salma Jeghloul** – Developer
- **Ayoub El Orf** – Developer
- **Ismail Dakir** – Developer

---

## 📜 License

This project is for educational purposes only.

Feel free to fork and modify it for learning or academic use.
