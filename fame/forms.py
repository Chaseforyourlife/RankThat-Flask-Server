from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField ,FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from fame.models import Category,Noun,User


class AddCategory(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=100)])
    picture = FileField('Add Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField("Submit")
    def validate_name(self, name):
        name = Category.query.filter_by(name=name.data).first()
        if name:
            raise ValidationError('That category name exists')




class AddNoun(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=60)])
    picture = FileField('Picture',validators=[FileAllowed(['jpg','png'])])
    description = StringField('Description', validators=[Length(min=0,max=60)])
    submit = SubmitField("Submit")


class SearchBar(FlaskForm):
    content= StringField('Search', validators=[DataRequired()])
    submit = SubmitField("Submit-Search")

class EditAccount(FlaskForm):
    name= StringField('Name', validators=[DataRequired()])
    submit = SubmitField("Submit")
    def validate_name(self, name):
        name = User.query.filter_by(name=name.data).first()
        if name:
            raise ValidationError('That name exists')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

    def validate_email(self,email):
        user= User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


'''
class AddPerson(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=60)])
    wiki= StringField('Wiki', validators=[])
    categories = StringField('Categories', validators=[])
    submit = SubmitField('Add Person')
    picture = FileField('Add Picture',validators=[FileAllowed(['jpg','png'])])
    def validate_wiki(self, wiki):
        person = Person.query.filter_by(wiki=wiki.data).first()
        if person:
            if person.wiki== "" or person.wiki==None:
                pass
            else:
                raise ValidationError('That wiki exsists')

class EditPerson(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=60)])
    wiki= StringField('Wiki', validators=[])
    categories = StringField('Categories', validators=[])
    picture = FileField('Update Picture',validators=[FileAllowed(['jpg','png'])])
    points = FloatField('Points', validators=[])
    submit = SubmitField('Submit Changes')

class AddCategory(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=60)])
    url_extension= StringField('URL', validators=[DataRequired()])
    picture = FileField('Update Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Add Category')

    def validate_url_extension(self, url_extension):
        category = Category.query.filter_by(url_extension=url_extension.data).first()
        if category:
            raise ValidationError('That url exists')
class EditCategory(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1,max=60)])
    url_extension= StringField('URL', validators=[DataRequired()])
    picture = FileField('Update Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Add Category')
'''
