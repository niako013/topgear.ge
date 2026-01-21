from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password: PasswordField = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class CarForm(FlaskForm):
    brand = StringField('ბრენდი', validators=[DataRequired()])
    model = StringField('მოდელი', validators=[DataRequired()])
    year = IntegerField('წელი', validators=[DataRequired()])
    description = TextAreaField('აღწერა', validators=[DataRequired()])
    # შევცვალეთ StringField ფაილის ასარჩევი ველით
    image = FileField('ავტომობილის ფოტო', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'მხოლოდ ფოტოები (jpg, png)!')
    ])
    description = TextAreaField('აღწერა', validators=[DataRequired()])
    submit = SubmitField('შენახვა')