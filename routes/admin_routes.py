from flask import Blueprint, render_template, request, redirect, flash, session
import json
from utils.decorators import role_required
from models.job_model import create_company, get_all_companies, create_job, get_all_jobs, get_placement_stats, get_recent_placements, get_placement_filter_options, get_applications_by_job, get_job_by_id, update_application_stage, bulk_update_application_status
from models.utility_model import create_notification, add_training_resource, get_all_notifications, get_all_training_resources, get_all_feedback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

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

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    selected_year = request.args.get('year', '').strip()
    selected_department = request.args.get('department', '').strip()

    selected_year = selected_year if selected_year.isdigit() else ''
    selected_department = selected_department or ''

    stats = get_placement_stats(year=selected_year or None, department=selected_department or None)
    recent_placements = get_recent_placements(year=selected_year or None, department=selected_department or None)
    filter_options = get_placement_filter_options()
    upcoming_drives = get_upcoming_drive_calendar()
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_placements=recent_placements,
        upcoming_drives=upcoming_drives,
        dept_data_json=json.dumps(stats['dept_data']),
        company_data_json=json.dumps(stats['company_data']),
        timeline_json=json.dumps(stats['timeline']),
        available_years=filter_options['years'],
        available_departments=filter_options['departments'],
        selected_year=selected_year,
        selected_department=selected_department,
    )

@admin_bp.route('/companies', methods=['GET', 'POST'])
@role_required('admin')
def companies():
    if request.method == 'POST':
        name = request.form.get('name')
        website_url = request.form.get('website_url')
        profile = request.form.get('profile')
        past_history = request.form.get('past_history')
        create_company(name, website_url, profile, past_history)
        flash('Company added successfully!', 'success')
        return redirect('/admin/companies')
        
    companies_list = get_all_companies()
    return render_template('admin/companies.html', companies=companies_list)

@admin_bp.route('/jobs', methods=['GET', 'POST'])
@role_required('admin')
def jobs():
    if request.method == 'POST':
        company_id = request.form.get('company_id')
        title = request.form.get('title')
        role = request.form.get('role')
        location = request.form.get('location')
        ctc = request.form.get('ctc')
        eligibility_criteria = request.form.get('eligibility_criteria')
        required_skills = request.form.get('required_skills')
        allowed_departments = ",".join(request.form.getlist('allowed_departments'))
        max_backlogs = request.form.get('max_backlogs', 0)
        min_cgpa = request.form.get('min_cgpa', 0.0)
        deadline = request.form.get('application_deadline')
        
        create_job(company_id, title, role, location, ctc, eligibility_criteria, required_skills, allowed_departments, max_backlogs, min_cgpa, deadline)
        flash('Job posted successfully!', 'success')
        return redirect('/admin/jobs')
        
    jobs_list = get_all_jobs()
    companies_list = get_all_companies()
    return render_template('admin/jobs.html', jobs=jobs_list, companies=companies_list)

@admin_bp.route('/job/<int:job_id>/applications')
@role_required('admin')
def job_applications(job_id):
    job = get_job_by_id(job_id)
    applications = get_applications_by_job(job_id)
    return render_template('admin/applications.html', job=job, applications=applications)

@admin_bp.route('/application/<int:app_id>/status', methods=['POST'])
@role_required('admin')
def update_application_status_route(app_id):
    new_stage = request.form.get('new_stage')
    job_id = request.form.get('job_id')
    if new_stage == 'Placed':
        new_stage = 'Selected'
    result = update_application_stage(app_id, new_stage)
    if result.get("email_sent"):
        flash("Application status updated and email sent to the student.", "success")
    elif result.get("email_configured"):
        flash("Application status updated, but the email could not be sent.", "warning")
    else:
        flash("Application status updated successfully.", "success")
    return redirect(f'/admin/job/{job_id}/applications')

@admin_bp.route('/job/<int:job_id>/applications/upload-status', methods=['POST'])
@role_required('admin')
def upload_application_status_csv_route(job_id):
    if 'csv_file' not in request.files:
        flash('No file part', 'danger')
        return redirect(f'/admin/job/{job_id}/applications')
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(f'/admin/job/{job_id}/applications')
    
    if file and file.filename.endswith('.csv'):
        from werkzeug.utils import secure_filename
        import os
        from config import Config
        
        filename = secure_filename(f"bulk_status_{job_id}_{file.filename}")
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        results = bulk_update_application_status(job_id, file_path)
        
        if "error" in results:
            flash(f"Error: {results['error']}", "danger")
        else:
            flash(f"Successfully updated {results['success']} applications. Failed: {results['failed']}", "success")
            if results['failed'] > 0:
                for detail in results['details']:
                    flash(detail, "warning")
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        flash('Please upload a valid CSV file.', 'danger')
        
    return redirect(f'/admin/job/{job_id}/applications')

@admin_bp.route('/utilities', methods=['GET', 'POST'])
@role_required('admin')
def utilities():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'notification':
            title = request.form.get('title')
            message = request.form.get('message')
            ntype = request.form.get('type')
            target_role = request.form.get('target_role')
            target_dept = request.form.get('target_dept')
            create_notification(title, message, ntype, target_role, target_dept)
            flash("Notification published", "success")
            
        elif action == 'training':
            title = request.form.get('title')
            desc = request.form.get('description')
            res_type = request.form.get('resource_type')
            url = request.form.get('url')
            add_training_resource(title, desc, res_type, url, session['user_id'])
            flash("Training resource added", "success")
            
        return redirect('/admin/utilities')
        
    training_list = get_all_training_resources()
    feedback_list = get_all_feedback()
    notifications_list = get_all_notifications(12)
    
    return render_template('admin/utilities.html', training=training_list, feedback=feedback_list, notifications=notifications_list)
