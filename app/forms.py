from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    SelectField,
    HiddenField,
    FileField,
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User


class ZipFileValidator(DataRequired):
    """
    Custom validator that checks if the uploaded file is .zip
    """

    def __call__(self, form, field):
        super().__call__(form, field)
        file = field.data
        filename = file.filename

        if not filename.lower().endswith(".zip"):
            message = "Invalid file format. Please upload a Zip file."
            raise ValidationError(message)


class LoginForm(FlaskForm):
    """
    Form for login inside the web app
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """

    Form for regristering inside the web app

    """

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please user a different username")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address")


class OpenFoamDictForm(FlaskForm):
    """
    Form for adding OpenFoam dictionary files to the web app
    TODO:DELETE

    """

    fname = StringField("Name of your file")
    dict_class = SelectField(
        "Type of file",
        choices=[
            ("blockMeshDict", "Block Mesh dict"),
            ("controlDict", "Control dict"),
            ("fvSolution", "fVSolution dict"),
            ("decomposeParDict", "decompose Par dict"),
            ("extrudeMeshDict", "Extrude Mesh dict"),
            ("other", "Other kind of file"),
        ],
        validators=[DataRequired()],
    )

    description = StringField("Describe the file if you want")
    fdata = FileField("Select a file", validators=[DataRequired()])
    submit = SubmitField("Add dictonary")


class OpenFoamSimForm(FlaskForm):
    """
    Form for adding OpenFoam simulations files

    """

    fname = StringField("Name of your simulation")
    description = StringField("Describe the simulation if you want")
    fdata = FileField("Select a .zip file", validators=[ZipFileValidator()])
    submit = SubmitField("Add simulation")


