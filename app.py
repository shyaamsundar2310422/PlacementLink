from flask import Flask, render_template, session, redirect
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.mentor_routes import mentor_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        if 'user_id' in session:
            role = session.get('role')
            if role == 'student':
                return redirect('/student/dashboard')
            elif role == 'mentor':
                return redirect('/mentor/dashboard')
            elif role == 'admin':
                return redirect('/admin/dashboard')
        return redirect('/auth/login')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
