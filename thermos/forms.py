from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.html5 import URLField
from wtforms.validators import DataRequired, url, Length, Email, Regexp, EqualTo,\
    url, ValidationError

from models import User


