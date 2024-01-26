"""
System forms
.Net Ninjas - 3/12/2021
Ellie Bruhns, Yifeng Cui, Cameron Jordal, Isaac Priddy, Nick Titzler
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Basic login form. Requires username and password to be entered."""
    username = StringField(
        "Username",
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
            
        ]
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField("Login")


class ResourceForm(FlaskForm):
    """Form for adding/removing books from database. Requires selection
    of a class, book, and action to take."""
    crn = StringField(
        "Class CRN",
        validators=[
            DataRequired()
        ]
    )
    isbn = StringField(
        "Book ISBN",
        validators=[
            DataRequired()
        ]
    )
    action = SelectField(
        "Action",
        validators=[
            DataRequired()
        ],
        choices=[
            ("add", "Add"),
            ("remove", "Remove")
        ]
    )
    submit = SubmitField("Submit")
