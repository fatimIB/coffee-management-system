# ☕ Coffee Management System

A **microservices-based coffee shop management system** built using **Python (Flask)**, **MySQL**, and **Docker**.  
This project demonstrates a distributed architecture where each feature of the system runs as an independent service, communicating through REST APIs.

---

## 🚀 Features

- **Login Service:** Handles user authentication (login/signup).
- **Menu Service:** Manages coffee menu items.
- **Order Service:** Handles customer orders.
- **Inventory Service:** Tracks stock and ingredients.
- **Cafe Service:** Manages cafe locations and details.
- **Analytics Service:** Generates sales and performance insights.
- **Gateway:** Acts as a central API gateway to route requests to other services.
- **Frontend:** A simple web interface to interact with all backend services.

---

## ⚙️ Technologies Used

- **Backend:** Python, Flask  
- **Database:** MySQL 8.0  
- **Containerization:** Docker & Docker Compose  
- **Frontend:** HTML, CSS, JavaScript (Vanilla or Framework)  
- **Communication:** REST APIs  
- **Version Control:** Git & GitHub  

---

## 🧩 Ports Overview

| Service              | Description                  | Port  |
|----------------------|------------------------------|-------|
| Gateway              | Main API gateway             | 5000  |
| Login Service        | Handles user authentication  | 5001  |
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
   cd coffee-management-system```
   
  2.Build and run the containers:
     ```bash
     docker-compose up --build


  3.Access the system:

    - Frontend: http://localhost:8080

    - Gateway API: http://localhost:5000

    - MySQL Database: localhost:3307

  4.Stop containers:
    ```bash
    docker-compose down
    
 ## 🧠 How It Works

 - Each service connects to the MySQL database through environment variables.

 - The gateway handles incoming requests and forwards them to the appropriate microservice.

 - The frontend communicates with the gateway only.

 - Data is initialized using init.sql during the first database setup.

## 🧑‍💻 Contributors

Fatima Iboubkarne – Project Lead & Developer

Team Members: 

## 📜 License

This project is for educational purposes only.
Feel free to fork and modify it for learning or academic use.



