from flask import Blueprint, render_template, request, redirect, flash, session
from werkzeug.utils import secure_filename
import os
from config import Config
from utils.decorators import role_required
from models.user_model import get_student_by_user_id
from models.profile_model import get_student_profile, create_update_request
from models.job_model import get_active_jobs, get_eligible_jobs, get_student_applications, apply_job
from models.utility_model import get_notifications_for_student, upload_document, get_student_documents, get_all_training_resources, submit_feedback

student_bp = Blueprint('student', __name__, url_prefix='/student')

def get_upcoming_drive_calendar():
    return [
        {
            "company": "Google",
            "date": "2026-04-08",
            "day": "Wed",
            "location": "Main Auditorium",
            "event": "Pre-placement talk and online assessment",
        },
        {
            "company": "Goldman Sachs",
            "date": "2026-04-15",
            "day": "Wed",
            "location": "Seminar Hall A",
            "event": "Aptitude test and technical screening",
        },
    ]

@student_bp.route('/dashboard')
@role_required('student')
def dashboard():
    student = get_student_by_user_id(session['user_id'])
    if not student:
        flash("Student record not found.", "danger")
        return redirect('/auth/login')
    
    profile = get_student_profile(student['id'])
    cgpa = float(profile['cgpa']) if profile and profile['cgpa'] else 0.0
    backlogs = int(profile['backlog_count']) if profile and profile['backlog_count'] else 0
    eligible_jobs = get_eligible_jobs(cgpa, backlogs, student['department'])
    notifications = get_notifications_for_student(student['department'])[:5]
    upcoming_drives = get_upcoming_drive_calendar()
    return render_template('student/dashboard.html', student=student, profile=profile, open_opportunity_count=len(eligible_jobs), notifications=notifications, upcoming_drives=upcoming_drives)

@student_bp.route('/profile', methods=['GET', 'POST'])
@role_required('student')
def profile():
    student = get_student_by_user_id(session['user_id'])
    profile = get_student_profile(student['id'])
    
    if request.method == 'POST':
        changes = {
            'cgpa': request.form.get('cgpa'),
            'skills': request.form.get('skills'),
            'projects': request.form.get('projects'),
            'certifications': request.form.get('certifications'),
            'backlog_count': request.form.get('backlog_count'),
            'contact_number': request.form.get('contact_number')
        }
        
        if student['mentor_id']:
            create_update_request(student['id'], student['mentor_id'], changes)
            flash('Profile update request sent to your mentor for approval.', 'success')
        else:
            flash('No mentor assigned to you yet. Please contact admin.', 'warning')
            
        return redirect('/student/profile')
        
    return render_template('student/profile.html', student=student, profile=profile)

@student_bp.route('/jobs')
@role_required('student')
def jobs():
    student = get_student_by_user_id(session['user_id'])
    profile = get_student_profile(student['id'])
    
    cgpa = float(profile['cgpa']) if profile and profile['cgpa'] else 0.0
    backlogs = int(profile['backlog_count']) if profile and profile['backlog_count'] else 0
    dept = student['department']
    browse_only = cgpa <= 0

    if browse_only:
        jobs_list = get_active_jobs()
    else:
        jobs_list = get_eligible_jobs(cgpa, backlogs, dept)
    
    applications = get_student_applications(student['id'])
    applied_job_ids = [app['job_id'] for app in applications] if applications else []

    return render_template('student/jobs.html', jobs=jobs_list, applied_job_ids=applied_job_ids, browse_only=browse_only)

@student_bp.route('/jobs/apply/<int:job_id>', methods=['POST'])
@role_required('student')
def apply_for_job(job_id):
    student = get_student_by_user_id(session['user_id'])
    
    success, msg = apply_job(student['id'], job_id)
    if success:
        flash("Successfully applied for the job!", "success")
    else:
        flash(f"Application failed: {msg}", "danger")
        
    return redirect('/student/jobs')

@student_bp.route('/applications')
@role_required('student')
def applications():
    student = get_student_by_user_id(session['user_id'])
    apps = get_student_applications(student['id'])
    return render_template('student/applications.html', applications=apps)

@student_bp.route('/resources')
@role_required('student')
def resources():
    student = get_student_by_user_id(session['user_id'])
    notifications = get_notifications_for_student(student['department'])
    training = get_all_training_resources()
    documents = get_student_documents(student['id'])
    
    return render_template('student/resources.html', 
                           notifications=notifications, 
                           training=training, 
                           documents=documents)

@student_bp.route('/upload_document', methods=['POST'])
@role_required('student')
def upload_doc():
    student = get_student_by_user_id(session['user_id'])
    doc_type = request.form.get('doc_type')
    
    if 'document_file' not in request.files:
        flash('No file part', 'danger')
        return redirect('/student/resources')
        
    file = request.files['document_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect('/student/resources')
        
    if file:
        filename = secure_filename(f"{student['register_number']}_{doc_type}_{file.filename}")
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        db_path = f"/static/uploads/{filename}"
        upload_document(student['id'], doc_type, db_path)
        flash(f'{doc_type} document uploaded successfully', 'success')
        
    return redirect('/student/resources')

@student_bp.route('/feedback', methods=['GET', 'POST'])
@role_required('student')
def feedback():
    student = get_student_by_user_id(session['user_id'])
    applications = get_student_applications(student['id'])
    
    past_jobs = [app for app in applications if app['stage'] == 'Selected']
    
    if request.method == 'POST':
        app_id = int(request.form.get('application_id'))
        selected_app = next((a for a in applications if a['application_id'] == app_id), None)
        
        if not selected_app:
            flash("Invalid application selected for feedback", "danger")
            return redirect('/student/feedback')
            
        from models.job_model import get_job_by_id
        job = get_job_by_id(selected_app['job_id'])
        
        interview_rating = request.form.get('interview_rating')
        company_rating = request.form.get('company_rating')
        difficulty = request.form.get('difficulty')
        suggestions = request.form.get('suggestions')
        
        submit_feedback(student['id'], job['company_id'], job['id'], interview_rating, company_rating, difficulty, suggestions)
        flash("Thank you for submitting your feedback!", "success")
        return redirect('/student/dashboard')
        
    return render_template('student/feedback.html', past_jobs=past_jobs)
