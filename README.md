# Cloud-Enabled Attendance System (Azure)

Role-based attendance monitoring system built with **Flask + PostgreSQL/Azure SQL**, deployed on **Microsoft Azure App Service**.

## Features
- Admin, Teacher, Student roles with separate dashboards
- Admin: manage users & generate attendance reports
- Teacher: create classes & mark attendance
- Student: view attendance & percentage
- Deployed on Azure App Service with Azure SQL Database
- Secure parameterized DB queries

## Architecture & Tech Stack
- **Backend:** Python (Flask)
- **Database:** Azure SQL Database / PostgreSQL
- **Frontend:** HTML, CSS, JS (Flask templates)
- **Cloud:** Microsoft Azure (App Service, SQL DB)
- **Other:** psycopg2 / pyodbc, virtualenv

## Repo Structure
```
cloud-attendance/
├─ app.py # main Flask app
├─ config.py 
├─ requirements.txt
├─ db/init_db.py # schema & sample inserts
├─ templates/ # HTML 
├─ static/ # CSS/JS
└─ README.md
```


## Azure Deployment

- Create Resource Group, Azure SQL DB, App Service
- Configure firewall + env vars in App Service
- Deploy via GitHub Actions / az webapp up

## Database Schema (summary)

- admins(username, name, password, email, phone)
- teachers(username, name, password, email, phone)
- students(id, name, email, class_sec, phone)
- classes(id, class_sec, name, date, teacher_username)
- attendance(id, class_id, student_id, status)


