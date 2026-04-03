import pymysql
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection
from utils.email_utils import send_application_status_email

_STOPWORDS = {
    "and", "or", "the", "a", "an", "to", "for", "of", "in", "on", "with", "by",
    "is", "are", "as", "at", "from", "be", "strong", "good", "skills", "skill",
    "knowledge", "understanding", "experience", "ability", "basic", "advanced"
}


def _normalize_text(value):
    text = (value or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(value):
    normalized = _normalize_text(value)
    return [token for token in normalized.split() if len(token) > 1 and token not in _STOPWORDS]


def _extract_required_skill_phrases(required_skills):
    if not required_skills:
        return []
    chunks = [chunk.strip() for chunk in re.split(r"[,;/]", required_skills) if chunk.strip()]
    return [_normalize_text(chunk) for chunk in chunks if _normalize_text(chunk)]


def _is_profile_jd_match(profile_text_normalized, profile_tokens, job):
    required_skill_phrases = _extract_required_skill_phrases(job.get("required_skills"))
    required_skill_tokens = set(_tokenize(" ".join(required_skill_phrases)))
    if not required_skill_tokens:
        return False, 0

    matched_required_tokens = len(required_skill_tokens.intersection(profile_tokens))
    skill_coverage = matched_required_tokens / len(required_skill_tokens)
    if skill_coverage < 0.45:
        return False, 0

    jd_text = " ".join([
        job.get("required_skills") or "",
        job.get("eligibility_criteria") or "",
        job.get("title") or "",
        job.get("role") or "",
    ])
    jd_tokens = set(_tokenize(jd_text))
    if not jd_tokens:
        return False, 0

    coverage = len(jd_tokens.intersection(profile_tokens)) / len(jd_tokens)
    strict_match = coverage >= 0.25
    return strict_match, round(((coverage + skill_coverage) / 2) * 100)


def get_jobs_matching_profile(student_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.department, sp.skills, sp.projects, sp.certifications
                FROM students s
                LEFT JOIN student_profiles sp ON sp.student_id = s.id
                WHERE s.id = %s
                """,
                (student_id,),
            )
            student_profile = cursor.fetchone()

            if not student_profile:
                return []

            profile_text = " ".join([
                student_profile.get("department") or "",
                student_profile.get("skills") or "",
                student_profile.get("projects") or "",
                student_profile.get("certifications") or "",
            ]).strip()

            profile_text_normalized = _normalize_text(profile_text)
            if not profile_text_normalized:
                return []

            profile_tokens = set(_tokenize(profile_text_normalized))
            if not profile_tokens:
                return []

            cursor.execute(
                """
                SELECT j.*, c.name as company_name, c.website_url
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.application_deadline >= CURDATE()
                ORDER BY j.created_at DESC
                """
            )
            jobs = cursor.fetchall()

        matched_jobs = []
        for job in jobs:
            matched, score = _is_profile_jd_match(profile_text_normalized, profile_tokens, job)
            if matched:
                job["match_score"] = score
                matched_jobs.append(job)

        matched_jobs.sort(key=lambda item: item.get("match_score", 0), reverse=True)
        return matched_jobs
    finally:
        connection.close()

def create_company(name, website_url, profile, past_history):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO companies (name, website_url, profile, past_history) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, website_url, profile, past_history))
        connection.commit()
    finally:
        connection.close()

def get_all_companies():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM companies ORDER BY name ASC")
            return cursor.fetchall()
    finally:
        connection.close()

def create_job(company_id, title, role, location, ctc, eligibility_criteria, required_skills, allowed_departments, max_backlogs, min_cgpa, application_deadline):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO jobs (company_id, title, role, location, ctc, eligibility_criteria, required_skills, allowed_departments, max_backlogs, min_cgpa, application_deadline) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (company_id, title, role, location, ctc, eligibility_criteria, required_skills, allowed_departments, max_backlogs, min_cgpa, application_deadline))
        connection.commit()
    finally:
        connection.close()

def get_all_jobs():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT j.*, c.name as company_name, c.website_url
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            ORDER BY j.created_at DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def get_active_jobs():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT j.*, c.name as company_name, c.website_url
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.application_deadline >= CURDATE()
            ORDER BY j.created_at DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()

def get_eligible_jobs(student_cgpa, student_backlogs, student_department):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT j.*, c.name as company_name, c.website_url
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.min_cgpa <= %s 
              AND j.max_backlogs >= %s
              AND (j.allowed_departments LIKE %s OR j.allowed_departments LIKE '%%All%%')
              AND j.application_deadline >= CURDATE()
            ORDER BY j.created_at DESC
            """
            dept_pattern = f"%{student_department}%"
            cursor.execute(sql, (student_cgpa, student_backlogs, dept_pattern))
            return cursor.fetchall()
    finally:
        connection.close()

def apply_job(student_id, job_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            matched_jobs = get_jobs_matching_profile(student_id)
            matched_job_ids = {job["id"] for job in matched_jobs}
            if job_id not in matched_job_ids:
                return False, "Your profile does not strictly match this job description."

            cursor.execute("SELECT id FROM applications WHERE student_id = %s AND job_id = %s", (student_id, job_id))
            if cursor.fetchone():
                return False, "Already applied to this job."
                
            sql = "INSERT INTO applications (student_id, job_id) VALUES (%s, %s)"
            cursor.execute(sql, (student_id, job_id))
            application_id = cursor.lastrowid
            
            status_sql = "INSERT INTO application_status (application_id, stage) VALUES (%s, 'Applied')"
            cursor.execute(status_sql, (application_id,))
            
        connection.commit()
        return True, "Successfully applied"
    except pymysql.MySQLError as e:
        return False, str(e)
    finally:
        connection.close()

def get_student_applications(student_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT a.id as application_id, a.job_id, a.applied_at, j.title, j.ctc, c.name as company_name, s.stage
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            JOIN application_status s ON s.application_id = a.id
            WHERE a.student_id = %s
            ORDER BY a.applied_at DESC
            """
            cursor.execute(sql, (student_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def get_applications_by_job(job_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT a.id as application_id, a.applied_at, st.first_name, st.last_name, st.register_number, st.department, p.cgpa, p.skills, p.resume_url, ast.stage
            FROM applications a
            JOIN students st ON a.student_id = st.id
            JOIN student_profiles p ON st.id = p.student_id
            JOIN application_status ast ON ast.application_id = a.id
            WHERE a.job_id = %s
            ORDER BY a.applied_at ASC
            """
            cursor.execute(sql, (job_id,))
            return cursor.fetchall()
    finally:
        connection.close()

def update_application_stage(application_id, stage):
    connection = get_db_connection()
    email_sent = False
    email_configured = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT stage FROM application_status WHERE application_id = %s", (application_id,))
            existing = cursor.fetchone()
            previous_stage = existing['stage'] if existing else None

            sql = "UPDATE application_status SET stage = %s WHERE application_id = %s"
            cursor.execute(sql, (stage, application_id))

            cursor.execute(
                """
                SELECT u.email, st.first_name, st.last_name, st.department,
                       c.name AS company_name, j.title
                FROM applications a
                JOIN students st ON a.student_id = st.id
                JOIN users u ON st.user_id = u.id
                JOIN jobs j ON a.job_id = j.id
                JOIN companies c ON j.company_id = c.id
                WHERE a.id = %s
                """,
                (application_id,)
            )
            application_details = cursor.fetchone()

            if application_details and previous_stage != stage:
                student_name = f"{application_details['first_name']} {application_details['last_name']}"
                from utils.email_utils import is_email_configured
                email_configured = is_email_configured()
                email_sent = send_application_status_email(
                    application_details["email"],
                    student_name,
                    application_details["company_name"],
                    application_details["title"],
                    stage,
                )

            if stage == 'Selected' and previous_stage != 'Selected':
                placement = application_details
                if placement:
                    from models.utility_model import create_notification
                    title = f"Placement Update: {placement['first_name']} placed at {placement['company_name']}"
                    message = (
                        f"{placement['first_name']} {placement['last_name']} has been selected for "
                        f"{placement['title']} at {placement['company_name']}."
                    )
                    create_notification(title, message, 'placement', 'all', placement['department'])
        connection.commit()
        return {
            "updated": True,
            "email_sent": email_sent,
            "email_configured": email_configured,
        }
    finally:
        connection.close()

def get_job_by_id(job_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT j.*, c.name as company_name, c.website_url
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.id = %s
            """
            cursor.execute(sql, (job_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def get_placement_stats():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT a.student_id, j.ctc, st.department, c.name as company_name 
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            JOIN students st ON a.student_id = st.id
            JOIN application_status ast ON ast.application_id = a.id
            WHERE ast.stage = 'Selected'
            """
            cursor.execute(sql)
            placements = cursor.fetchall()
            
            cursor.execute("SELECT count(*) as total FROM students")
            total_students_row = cursor.fetchone()
            total_students = total_students_row['total'] if total_students_row and total_students_row['total'] > 0 else 1
            
            stats = {
                'total_placed': len(placements),
                'placement_percentage': int((len(placements) / total_students) * 100),
                'highest_ctc': 0,
                'average_ctc': 0,
                'dept_data': {},
                'company_data': {}
            }
            
            total_ctc = 0
            valid_ctc_count = 0
            
            for p in placements:
                dept = p['department']
                stats['dept_data'][dept] = stats['dept_data'].get(dept, 0) + 1
                
                company = p['company_name']
                stats['company_data'][company] = stats['company_data'].get(company, 0) + 1
                
                try:
                    val = p['ctc'].lower().replace('lpa', '').strip()
                    num = float(val)
                    if num > stats['highest_ctc']:
                        stats['highest_ctc'] = num
                    total_ctc += num
                    valid_ctc_count += 1
                except:
                    pass
                    
            if valid_ctc_count > 0:
                stats['average_ctc'] = round(total_ctc / valid_ctc_count, 2)
                
            return stats
    finally:
        connection.close()

def get_recent_placements(limit=8):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT st.first_name, st.last_name, st.register_number, st.department,
                   c.name AS company_name, j.title, j.location, j.ctc, ast.updated_at
            FROM applications a
            JOIN students st ON a.student_id = st.id
            JOIN jobs j ON a.job_id = j.id
            JOIN companies c ON j.company_id = c.id
            JOIN application_status ast ON ast.application_id = a.id
            WHERE ast.stage = 'Selected'
            ORDER BY ast.updated_at DESC
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
    finally:
        connection.close()
