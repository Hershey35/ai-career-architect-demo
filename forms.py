from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,IntegerField,FileField
from wtforms.validators import Length,Email,EqualTo,DataRequired,ValidationError
from models import User
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
class RegisterForm(FlaskForm):
    # def validate_username(self,username_to_check):
    #     user = User.query.filter_by(username=email_address_to_check.data).first()
    #     if user:
    #         raise ValidationError('Username already exiss! Please try a different username')

    def validate_email_address(self,email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email address already exiss! Please try a different email addres')
    fullname = StringField(label='Name:',validators=[Length(min=2,max=30),DataRequired()])    
    email_address = StringField(label='Email Address:',validators=[Email(),DataRequired()])
    password1 = PasswordField(label='Password:',validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Confirm Password:',validators=[EqualTo('password1'),DataRequired()])

    submit = SubmitField(label='Create Account')
    
class LoginForm(FlaskForm):
    email_address=StringField(label='Email Address:',validators=[DataRequired()])
    password=StringField(label='Password:',validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class UploadResumeForm(FlaskForm):
    resume_file = FileField("Upload Resume", validators=[DataRequired()])
    submit = SubmitField("Upload")

class MatchResumeToJDForm(FlaskForm):
    resume_id = SelectField('Select Resume', coerce=int, validators=[DataRequired()])
    job_description = TextAreaField('Paste Job Description', validators=[DataRequired()])
    submit = SubmitField('Match Resume')

class TailorResumeForm(FlaskForm):
    resume_id = SelectField('Select Resume', coerce=int, validators=[DataRequired()])
    job_description = TextAreaField('Paste Job Description', validators=[DataRequired()])
    submit = SubmitField('Generate Tailored Resume & Cover Letter')
