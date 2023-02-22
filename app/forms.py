from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField,HiddenField
from wtforms.validators import DataRequired,ValidationError,Email,EqualTo
from app.models import User


class LoginForm(FlaskForm):
    """
    Form for login inside the web app
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """
    
    Form for regristering inside the web app

    """
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    password2 = PasswordField(
            'Repeat Password',validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self,username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError("Please user a different username")

    def validate_email(self,email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address")

class OpenFoamForm(FlaskForm):
    """
    Form for adding OpenFoam files to the web app


    """
    fname = StringField('Name of your file')
    fclass = SelectField('Type of file',
                             choices = [('blockMeshDict','Block Mesh dict'),
                                        ('controlDict','Control dict'),
                                        ('fvSolution','fVSolution dict'),
                                        ('decomposeParDict','decompose Par dict'),
                                        ('extrudeMeshDict','Extrude Mesh dict'),

                                        ('other','Other kind of file')
                                        ],
                             validators=[DataRequired()])
    
    description = StringField('Describe the file if you want')
    fdata = StringField('Add the dictonary to the web app',validators=[DataRequired()])
    submit = SubmitField('Add dictonary')

    
