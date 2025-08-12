from main import app,db
from flask import render_template,redirect,url_for,flash,request,abort,send_file,session
from models import User,UploadedResume
from forms import RegisterForm,LoginForm,UploadResumeForm,MatchResumeToJDForm,TailorResumeForm
from flask_login import login_user,logout_user,login_required,current_user
import os
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from AI_Logic import resume_parser,matching_logic,resume_coverletter,utils,resume_parser_test
from sqlalchemy import func
import numpy as np
from sqlalchemy import func
import json

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(fullname=form.fullname.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account created successfully! You are now logged in as: {user_to_create.fullname}', category='success')

        return redirect(url_for('home_page'))
    if form.errors != {}:#If there are  errors from validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}',category='danger')
        
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.fullname}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!",category='info')
    return redirect(url_for("home_page"))


app.config['UPLOAD_FOLDER'] = 'uploaded_resumes'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    form = UploadResumeForm()
    parsed_result = {}

    if form.validate_on_submit():
        resume_file = request.files.get('resume_file')

        if resume_file:
            filename = secure_filename(resume_file.filename)
            file_contents = resume_file.read()

            parsed_result = resume_parser_test.resume_combine_parser(io.BytesIO(file_contents), filename)

            if not parsed_result:
                flash('Failed to extract raw text from resume.', category='danger')
                return redirect(request.url)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'wb') as f:
                f.write(file_contents)

            uploaded = UploadedResume(
                user_id=current_user.id,
                file_path=file_path,
                parsed_text=parsed_result.get("full_text", ""),
                skills="\n".join(parsed_result.get("skills", [])) if isinstance(parsed_result.get("skills", []), list) else parsed_result.get("skills", ""),
                education="\n".join(parsed_result.get("education", [])) if isinstance(parsed_result.get("education", []), list) else parsed_result.get("education", ""),
                experience="\n".join(parsed_result.get("experience", [])) if isinstance(parsed_result.get("experience", []), list) else parsed_result.get("experience", ""),
                achievements="\n".join(parsed_result.get("achievements", [])) if isinstance(parsed_result.get("achievements", []), list) else parsed_result.get("achievements", ""),
            )
            db.session.add(uploaded)
            db.session.commit()
            flash('Resume uploaded and parsed successfully!', category='success')

        else:
            flash('Invalid file type. Please upload a PDF or DOCX.', category='danger')
            return redirect(request.url)

    return render_template('uploaded_resume.html', form=form, parsed_result=parsed_result)


@app.route('/my_resumes')
@login_required
def my_resumes():
    resumes = UploadedResume.query.filter_by(user_id=current_user.id).order_by(UploadedResume.id.desc()).all()
    return render_template('my_resumes.html', resumes=resumes)

@app.route('/view_resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    resume = UploadedResume.query.get_or_404(resume_id)
    # Prevent other users from accessing files
    if resume.user_id != current_user.id:
        abort(403)
    return send_file(resume.file_path)  # Opens in browser (if supported)

@app.route('/match_resume_to_jd', methods=['GET', 'POST'])
@login_required
def match_resume_to_jd_route():
    form = MatchResumeToJDForm()

    form.resume_id.choices = [
        (r.id, os.path.basename(r.file_path)) 
        for r in UploadedResume.query.filter_by(user_id=current_user.id).all()
    ]

    match_score = None

    if form.validate_on_submit():
        resume = UploadedResume.query.get(form.resume_id.data)
        jd_text = form.job_description.data
        match_score = matching_logic.match_resume_to_jd_openai(resume.parsed_text, jd_text)

    return render_template(
        'match_resume_to_jd.html',
        form=form,
        match_score=match_score
    )

@app.route('/tailor_resume', methods=['GET', 'POST'])
@login_required
def tailor_resume():
    form = TailorResumeForm()

    user_resumes = UploadedResume.query.filter_by(user_id=current_user.id).all()
    form.resume_id.choices = [(r.id, os.path.basename(r.file_path)) for r in user_resumes]

    tailored_resume = None
    cover_letter = None

    if form.validate_on_submit():
        resume = UploadedResume.query.get(form.resume_id.data)
        jd_text = form.job_description.data
        tailored_resume, cover_letter = resume_coverletter.generate_tailored_resume_and_cover_letter(
            resume.parsed_text,
            jd_text
        )

        # Save to session for download routes
        session['tailored_resume'] = tailored_resume
        session['cover_letter'] = cover_letter

    return render_template(
        'tailor_resume.html',
        form=form,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter
    )

@app.route('/download_tailored/<format>')
@login_required
def download_tailored(format):
    resume_text = session.get('tailored_resume')
    cover_letter_text = session.get('cover_letter')

    if not resume_text or not cover_letter_text:
        flash("No tailored resume to download.", "danger")
        return redirect(url_for('tailor_resume'))

    if format == 'docx':
        buffer = utils.export_docx(resume_text, cover_letter_text)
        return send_file(buffer, as_attachment=True,
                         download_name="Tailored_Resume_and_Cover_Letter.docx",
                         mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    elif format == 'pdf':
        buffer = utils.export_pdf(resume_text, cover_letter_text)
        return send_file(buffer, as_attachment=True,
                         download_name="Tailored_Resume_and_Cover_Letter.pdf",
                         mimetype="application/pdf")
    else:
        flash("Invalid file format.", "danger")
        return redirect(url_for('tailor_resume'))

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    # Restrict to admins only
    if not getattr(current_user, "is_admin", False):
        abort(403)  # Or return redirect(url_for("home"))

    total_uploads = UploadedResume.query.count()

    uploads_by_date_raw = db.session.query(
        func.date(UploadedResume.upload_timestamp),
        func.count(UploadedResume.id)
    ).group_by(func.date(UploadedResume.upload_timestamp)).all()

    uploads_by_date = [
        [str(date), count] for date, count in uploads_by_date_raw
    ]

    skills_data = UploadedResume.query.with_entities(UploadedResume.skills).all()
    skill_counter = {}
    for row in skills_data:
        if row.skills:
            for skill in row.skills.split(","):
                skill = skill.strip().lower()
                skill_counter[skill] = skill_counter.get(skill, 0) + 1

    top_skills = sorted(skill_counter.items(), key=lambda x: x[1], reverse=True)[:10]

    return render_template(
        "admin_dashboard.html",
        total_uploads=total_uploads,
        uploads_by_date=uploads_by_date,
        top_skills=top_skills
    )
