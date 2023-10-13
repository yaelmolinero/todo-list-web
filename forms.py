from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class RegisterUser(FlaskForm):
    username = StringField("Name", [DataRequired()])
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired(), Length(4, 16)])

    submit = SubmitField("Sign Up")

class LoginUser(FlaskForm):
    email = EmailField("Email", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])

    submit = SubmitField("Log In")
