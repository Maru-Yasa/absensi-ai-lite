from flask_wtf.file import FileAllowed, FileRequired
from flask_wtf import FlaskForm
from wtforms import StringField, validators, FileField


class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=255)])
    name = StringField('Nama', [validators.Length(min=2, max=255)])
    face = FileField("Foto Diri", validators=[FileRequired(), FileAllowed(['png', 'jpg', 'jpeg'])])
