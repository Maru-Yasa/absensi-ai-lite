from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
from wtforms import FileField


class AttendanceForm(FlaskForm):
    face = FileField(validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
