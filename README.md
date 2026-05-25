# ⚙️ KinesioPro - Backend API (Clinical Management System)

<div align="center">
  <img width="984" height="478" alt="image" src="https://github.com/user-attachments/assets/4d1eece2-9f4f-46e5-8051-ce372a0dd13a" />
</div>

## 📖 Overview
This repository contains the RESTful API and core business logic for KinesioPro, a clinical management system. Built with high performance in mind, this backend handles secure authentication, strict data validation, and database interactions using an asynchronous architecture.

## ✨ Core Functionalities
* 🛡️ **Stateless Security:** JWT (JSON Web Tokens) authentication with Bcrypt password hashing.
* 🚦 **Business Logic Validation:** Robust endpoint validation preventing critical errors, such as double-booking appointments (overlapping schedules).
* 🗄️ **Relational Integrity:** Normalized database architecture (3NF) ensuring referential integrity between users, patients, and medical records.
* 📄 **Auto-generated Documentation:** Interactive API documentation using Swagger UI.

## 🛠️ Tech Stack
* **Language/Framework:** Python, FastAPI 
* **Database:** MySQL 8.0 
* **ORM:** SQLAlchemy 
* **Data Validation:** Pydantic 
* **Security:** JWT, Bcrypt, CORS Configuration 

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone [https://github.com/lucasaguero23/kinesiopro-backend.git](https://github.com/lucasaguero23/kinesiopro-backend.git)
   ```

2. Navigate to the project directory:
   
   ```bash
   cd kinesiopro-backend
   ```

3. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Set up your .env file with your MySQL database credentials.

6. Run the server:

   ```bash
   uvicorn main:app --reload
   ```
