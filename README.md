# 🎓 HaziriPro – AI-Based Smart Attendance System with Emotion Detection

<p align="center">
  <img src="static/favicon.ico" alt="HaziriPro Logo" width="120"/>
</p>

<p align="center">
  <strong>Final Year Project (FYP)</strong><br>
  BS Software Engineering<br>
  University of Management and Technology (UMT), Lahore
</p>

---

## Project Overview

**HaziriPro** is an AI-powered Smart Attendance Management System developed to automate employee attendance using **Face Recognition** and **Emotion Detection** technologies. The system eliminates manual attendance processes, enhances accuracy, and provides HR departments with valuable insights into employee attendance and emotional trends.

The application is built using **Flask**, **OpenCV**, **DeepFace**, **Face Recognition**, and **SQLite**, providing a modern web-based solution for attendance management.

---

# Key Features

### Authentication & Role-Based Access Control
- Secure Login System
- Role-Based Access Control (RBAC)
- Admin Dashboard
- HR Dashboard
- Employee Dashboard
- Manager Dashboard

---

### Employee Management

- Add Employee
- Edit Employee
- Delete Employee
- Employee Profile
- Department Assignment
- Profile Photo Upload
- Automatic Employee ID Generation

---

### Face Recognition Attendance

- Face Registration
- Face Encoding Storage
- Real-Time Face Recognition
- Check-In
- Check-Out
- Duplicate Attendance Prevention
- Attendance History

---

### Emotion Detection

Using **DeepFace** with RetinaFace:

- Happy
- Sad
- Angry
- Neutral
- Fear
- Surprise
- Disgust

Emotion data is automatically recorded during attendance.

---

###  Department Management

- Create Department
- Edit Department
- Delete Department
- View Department Employees

---

### Reports & Analytics

- Attendance Reports
- CSV Export
- Excel Export
- PDF Export
- HR Dashboard Analytics

---

### Payroll Module

- Salary Management
- Payroll Dashboard
- Payslip Generation

---

### Leave Management

- Leave Requests
- Leave Approval
- Leave Tracking

---

### HR Chatbot

Built-in chatbot to assist HR users with common attendance and employee-related queries.

---

# AI Technologies Used

- Face Recognition
- Face Encoding
- Emotion Detection
- DeepFace
- RetinaFace
- OpenCV

---

# Technologies Used

## Backend

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate

## Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

## Database

- SQLite
- SQLAlchemy ORM

## Artificial Intelligence

- OpenCV
- DeepFace
- Face Recognition
- Dlib
- RetinaFace
- TensorFlow
- Keras

## Data Processing

- Pandas
- NumPy
- Scikit-learn

---

# Project Structure

```text
HaziriPro
│
├── ai/
├── models/
├── routes/
├── services/
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
├── utils/
├── exports/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
└── README.md
```

---

# Installation

### Clone Repository

```bash
git clone https://github.com/ZunairShakoor/HaziriPro.git
```

```bash
cd HaziriPro
```

---

### Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Initialize Database

```bash
python init_db.py
```

---

### Run Application

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# Modules

- Authentication
- Employee Management
- Department Management
- Attendance Management
- Face Recognition
- Emotion Detection
- Payroll
- Leave Management
- Reports
- HR Chatbot

---

# Security Features

- Password Hashing
- Session Management
- Role-Based Access Control
- Login Protection
- Secure Face Verification

---

# Future Enhancements

- Mobile Application
- Cloud Database Integration
- Multi-Camera Support
- GPS Attendance
- QR Code Attendance
- Email Notifications
- Push Notifications
- Biometric Device Integration

---

# Team Members

| Name | Role |
|------|------|
| **Zunair Shakoor** | Backend/Frontend |
| **Anum Niaz** | Backend/Frontend |
| **Fiza** | Testing & QA |
| **Eman Azam** | Documentation |


---

# Supervisor

**Supervisor**

*Mr. Waqar Ashiq.*

---

# Academic Information

**University:** University of Management and Technology (UMT), Lahore

**Department:** Software Engineering

**Degree:** BS Software Engineering

**Project Type:** Final Year Project (FYP)

---

# License

This project was developed for academic purposes as a Final Year Project at the University of Management and Technology (UMT).

---

#  Acknowledgements

Special thanks to our supervisor ( Waqar Ashiq)and the open-source community whose libraries and frameworks made this project possible.

---

<p align="center">
Made with  using Flask, OpenCV, DeepFace and Python
</p>