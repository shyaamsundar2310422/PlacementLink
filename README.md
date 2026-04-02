🧠 PlacementLink
Intelligent Placement & Career Development Management System

PlacementLink is a Flask + MySQL based web application designed to streamline and automate the college placement process. It provides a centralized platform for students, mentors, and administrators to manage the entire placement lifecycle efficiently.

🚀 Features
👨‍🎓 Student
Register and log in using email or username
Complete and update profile
Browse job opportunities (even with incomplete profile)
Apply for jobs and track application status
Upload resume and supporting documents
Receive notifications and placement updates
Submit post-placement feedback
👨‍🏫 Mentor
View assigned students
Access student profiles
Approve or reject profile update requests
🛠️ Admin
Manage companies and job postings
View applicants and update application stages
Send notifications and broadcast messages
Add training resources
View placement analytics and reports
🏗️ System Architecture

The system follows a multi-tier architecture:

Frontend: HTML5, CSS3, JavaScript
Backend: Python (Flask Framework)
Database: MySQL
Layers:
Presentation Layer – User interfaces and dashboards
Application Layer – Business logic and workflow handling
Data Layer – Database and data management
Analytics Layer – Insights and reporting
🧩 Backend Structure (Flask Blueprints)

The backend is modularized using Flask Blueprints:

auth_routes.py – Authentication and user management
student_routes.py – Student functionalities
mentor_routes.py – Mentor operations
admin_routes.py – Admin controls
🗄️ Database Design

Key tables include:

users – Authentication and roles
profiles – Student details
companies & jobs – Job listings
applications – Job applications
application_status – Status tracking
notifications – Alerts and updates
documents – Resume and uploads
training_resources – Learning materials
feedback – Post-placement feedback
🔐 Authentication & Authorization
Login via email/username and password
Session-based authentication using Flask
Role-based access control (Student, Mentor, Admin)
Secure route handling based on user roles
⚙️ Key Functional Highlights
Transactional student registration
Automatic mentor assignment
Flexible job browsing for incomplete profiles
Real-time application tracking
Email and in-app notification system
Centralized placement operations dashboard
🎯 Job Eligibility Logic

Based on:

Academic performance (CGPA)
Skills and qualifications
Branch or specialization

Ensures only eligible candidates apply for jobs

🤖 Machine Learning Integration
Algorithm: Logistic Regression
Used to predict placement readiness
Based on academic and skill-related data
Provides probability-based insights
🔄 Workflow
Student registration and profile creation
Eligibility evaluation
Job browsing and application submission
Application review and status updates
Selection or rejection outcome
Feedback collection and analytics
🛠️ Installation & Setup

Follow the steps below to run the project locally:

📌 Prerequisites
Python 3.11 installed
MySQL Server installed and running
Git installed
⚙️ Setup Steps
# Navigate to project directory
cd "C:\Placement App\college_placement_system"

# Create virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python .\database\init_db.py

# Seed sample data
python .\seed_database.py

# Run the application
python .\app.py
🗄️ Database Configuration

Ensure MySQL server is running. Update your database credentials in the configuration file (e.g., config.py)

Example:
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "placement_db"
🌐 Access the Application

Open your browser and go to:
👉 http://127.0.0.1:5000/

⚠️ Notes
Make sure the virtual environment is activated before running the app
If PowerShell blocks execution, run:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
📈 Future Enhancements
JWT-based authentication
REST API integration
AI-based job recommendation system
Resume parsing and skill extraction
Cloud deployment (Docker, AWS/GCP)
Advanced analytics dashboard
👥 Team
Shyaam Sundar M
Srivignesh R
Sushmidha S
Swetha V
Venkata Navadeep Reddy
Yaazhini A
📌 Conclusion

PlacementLink provides a centralized, scalable, and efficient solution for managing placement activities. It enhances transparency, improves communication, and enables data-driven decision-making to boost placement success rates.
