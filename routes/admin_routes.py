from flask import Blueprint, render_template, request, redirect, flash, session
import json
from utils.decorators import role_required
from models.job_model import create_company, get_all_companies, create_job, get_all_jobs, get_placement_stats, get_recent_placements, get_applications_by_job, get_job_by_id, update_application_stage
from models.utility_model import create_notification, add_training_resource, get_all_notifications, get_all_training_resources, get_all_feedback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    stats = get_placement_stats()
    recent_placements = get_recent_placements()
    return render_template('admin/dashboard.html', stats=stats, recent_placements=recent_placements, dept_data_json=json.dumps(stats['dept_data']), company_data_json=json.dumps(stats['company_data']))

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
    result = update_application_stage(app_id, new_stage)
    if result.get("email_sent"):
        flash("Application status updated and email sent to the student.", "success")
    elif result.get("email_configured"):
        flash("Application status updated, but the email could not be sent.", "warning")
    else:
        flash("Application status updated. Email was not sent because SMTP is not configured yet.", "warning")
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
