<h1 align="center"> PlacementLink</h1>
<h3 align="center">Intelligent Placement & Career Development Management System</h3>

<p align="center">
A Flask + MySQL based web application to streamline and automate the college placement process.
</p>

<hr>

<h2> Features</h2>

<h3> Student</h3>
<ul>
<li>Register and log in using email or username</li>
<li>Complete and update profile</li>
<li>Browse job opportunities (even with incomplete profile)</li>
<li>Apply for jobs and track application status</li>
<li>Upload resume and supporting documents</li>
<li>Receive notifications and placement updates</li>
<li>Submit post-placement feedback</li>
</ul>

<h3> Mentor</h3>
<ul>
<li>View assigned students</li>
<li>Access student profiles</li>
<li>Approve or reject profile update requests</li>
</ul>

<h3> Admin</h3>
<ul>
<li>Manage companies and job postings</li>
<li>View applicants and update application stages</li>
<li>Send notifications and broadcast messages</li>
<li>Add training resources</li>
<li>View placement analytics and reports</li>
</ul>

<hr>

<h2> System Architecture</h2>

<p><b>Frontend:</b> HTML5, CSS3, JavaScript<br>
<b>Backend:</b> Python (Flask Framework)<br>
<b>Database:</b> MySQL</p>

<h3>Layers</h3>
<ul>
<li><b>Presentation Layer</b> – User interfaces and dashboards</li>
<li><b>Application Layer</b> – Business logic and workflow handling</li>
<li><b>Data Layer</b> – Database and data management</li>
<li><b>Analytics Layer</b> – Insights and reporting</li>
</ul>

<hr>

<h2> Backend Structure (Flask Blueprints)</h2>

<ul>
<li><b>auth_routes.py</b> – Authentication and user management</li>
<li><b>student_routes.py</b> – Student functionalities</li>
<li><b>mentor_routes.py</b> – Mentor operations</li>
<li><b>admin_routes.py</b> – Admin controls</li>
</ul>

<hr>

<h2> Database Design</h2>

<ul>
<li>users – Authentication and roles</li>
<li>profiles – Student details</li>
<li>companies & jobs – Job listings</li>
<li>applications – Job applications</li>
<li>application_status – Status tracking</li>
<li>notifications – Alerts and updates</li>
<li>documents – Resume and uploads</li>
<li>training_resources – Learning materials</li>
<li>feedback – Post-placement feedback</li>
</ul>

<hr>

<h2> Authentication & Authorization</h2>

<ul>
<li>Login using email/username and password</li>
<li>Session-based authentication using Flask</li>
<li>Role-based access control (Student, Mentor, Admin)</li>
<li>Secure route handling based on user roles</li>
</ul>

<hr>

<h2> Key Functional Highlights</h2>

<ul>
<li>Transactional student registration</li>
<li>Automatic mentor assignment</li>
<li>Flexible job browsing for incomplete profiles</li>
<li>Real-time application tracking</li>
<li>Email and in-app notification system</li>
<li>Centralized placement operations dashboard</li>
</ul>

<hr>

<h2> Job Eligibility Logic</h2>

<ul>
<li>Academic performance (CGPA)</li>
<li>Skills and qualifications</li>
<li>Branch or specialization</li>
</ul>

<p><b>Ensures only eligible candidates can apply for jobs</b></p>

<hr>

<h2> Machine Learning Integration</h2>

<ul>
<li><b>Algorithm:</b> Logistic Regression</li>
<li>Predicts placement readiness</li>
<li>Based on academic and skill-related data</li>
<li>Provides probability-based insights</li>
</ul>

<hr>

<h2> Workflow</h2>

<ul>
<li>Student registration and profile creation</li>
<li>Eligibility evaluation</li>
<li>Job browsing and application submission</li>
<li>Application review and status updates</li>
<li>Selection or rejection outcome</li>
<li>Feedback collection and analytics</li>
</ul>

<hr>

<h2> Installation & Setup</h2>

<pre>
# Clone the repository
git clone https://github.com/shyaamsundar2310422/placementlink.git
cd placementlink

# Create virtual environment
py -3.11 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Initialize database
python .\database\init_db.py

# Seed sample data (optional)
python .\seed_database.py

# Run the application
python .\app.py
</pre>

<hr>

<h2> Database Configuration</h2>

<p>Ensure MySQL server is running. Update your database credentials in <b>config.py</b></p>

<pre>
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "placement_db"
</pre>

<hr>

<h2> Access the Application</h2>

<p>Open your browser and go to:</p>

<p><b>http://127.0.0.1:5000/</b></p>

<hr>

<h2> Notes</h2>

<ul>
<li>Make sure the virtual environment is activated before running the application</li>
<li>Ensure MySQL service is running</li>
<li>If PowerShell blocks execution:</li>
</ul>

<pre>
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
</pre>

<hr>

python .\database\init_db.py
python .\seed_database.py
python .\app.py
</pre>

<hr>

<h2> Database Configuration</h2>

<pre>
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"
DB_NAME = "placement_db"
</pre>

<hr>

<h2> Access the Application</h2>

<p>http://127.0.0.1:5000/</p>

<hr>

<h2> Notes</h2>

<ul>
<li>Activate the virtual environment before running</li>
<li>If PowerShell blocks execution:</li>
</ul>

<pre>
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
</pre>

<hr>

<h2> Future Enhancements</h2>

<ul>
<li>JWT-based authentication</li>
<li>REST API integration</li>
<li>AI-based job recommendation system</li>
<li>Resume parsing and skill extraction</li>
<li>Cloud deployment (Docker, AWS/GCP)</li>
<li>Advanced analytics dashboard</li>
</ul>

<hr>

<h2> Team</h2>

<ul>
<li>Shyaam Sundar M</li>
<li>Srivignesh R</li>
<li>Sushmidha S</li>
<li>Swetha V</li>
<li>Venkata Navadeep Reddy</li>
<li>Yaazhini A</li>
</ul>

<hr>

<h2> Conclusion</h2>

<p>
PlacementLink provides a <b>centralized, scalable, and efficient solution</b> for managing placement activities. 
It enhances transparency, improves communication, and enables <b>data-driven decision-making</b> to boost placement success rates.
</p>
