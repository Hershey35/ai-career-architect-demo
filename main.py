from flask import Flask, render_template
from flask import Flask, render_template, request, redirect
from models.database import db, UserProfile, GeneratedDocument
from models.resume_generator import generate_resume_and_cover_letter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career_architect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        profile = UserProfile(
            full_name=request.form['full_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            education=request.form['education'],
            experience=request.form['experience'],
            skills=request.form['skills'],
            achievements=request.form['achievements']
        )
        db.session.add(profile)
        db.session.commit()
        return redirect(f'/upload-jd/{profile.id}')
    return render_template('profile.html')

@app.route('/upload-jd/<int:user_id>', methods=['GET', 'POST'])
def upload_jd(user_id):
    if request.method == 'POST':
        jd = request.form['job_description']
        user = UserProfile.query.get(user_id)        
        resume, cover = generate_resume_and_cover_letter(user, jd)
        doc = GeneratedDocument(
            user_id=user_id,
            job_description=jd,
            resume_text=resume,
            cover_letter_text=cover
        )
        db.session.add(doc)
        db.session.commit()
        return render_template('result.html', resume=resume, cover_letter=cover)

    return render_template('upload_jd.html', user_id=user_id)


if __name__ == "__main__":
    app.run(debug=True)